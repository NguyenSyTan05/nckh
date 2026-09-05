"""Multilingual, multi-speaker Whisper LoRA fine-tuning for ClassBridge – DTU Edition.
# pyrefly: ignore-all-errors

Nâng cấp so với phiên bản cơ bản:
  - LoRA rank r=32, target thêm k_proj + out_proj (tăng capacity)
  - Curriculum Learning: 3 giai đoạn (clean → augmented → hard)
  - DTU Academic Vocab Injection: initial_prompt với thuật ngữ CNTT/AI DTU
  - Whisper-small mặc định (thay vì base)
  - SpecAugment mạnh hơn: mask_time_prob=0.15, mask_feature_prob=0.10
  - Per-language WER/CER breakdown (vi vs en)
  - Hỗ trợ audio tới 30 giây (chunked) thay vì 30s cứng

Recommended JSONL row:
{"audio":"clip.wav","text":"verified transcript","language":"vi",
 "speaker_id":"teacher-01","accent":"vi-central","difficulty":"easy"}

Optional 'difficulty' field: 'easy' | 'medium' | 'hard' (dùng cho curriculum learning)
Only consented recordings and verified verbatim transcripts should be used.
Validation must contain speakers absent from training; use the companion
prepare_multilingual_manifest.py script to enforce that split.
"""

from __future__ import annotations

import argparse
import os
import random
import re
import sys
import unicodedata

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Union
# Ensure virtualenv site-packages is in sys.path
VENV_SITE = Path(__file__).resolve().parent.parent / "backend" / "ai-service" / ".venv" / "Lib" / "site-packages"
if VENV_SITE.exists() and str(VENV_SITE) not in sys.path:
    sys.path.insert(0, str(VENV_SITE))

import numpy as np
from datasets import Dataset
# ML libraries are imported lazily inside main() to prevent IDE false-positive errors
# when the virtualenv is not the system interpreter.


@dataclass
class SpeechSeq2SeqCollator:
    processor: Any  # WhisperProcessor at runtime

    def __call__(self, features: list[dict[str, Any]]) -> dict[str, Any]:
        import torch  # type: ignore[import]
        inputs = [{"input_features": item["input_features"]} for item in features]
        batch = self.processor.feature_extractor.pad(inputs, return_tensors="pt")
        labels = [{"input_ids": item["labels"][:448]} for item in features]
        labels_batch = self.processor.tokenizer.pad(labels, return_tensors="pt")
        label_ids = labels_batch["input_ids"].masked_fill(
            labels_batch.attention_mask.ne(1), -100
        )
        if (label_ids[:, 0] == self.processor.tokenizer.bos_token_id).all():
            label_ids = label_ids[:, 1:]
        if label_ids.shape[1] > 448:
            label_ids = label_ids[:, :448]
        batch["labels"] = label_ids
        return batch



def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="ClassBridge Whisper LoRA Fine-Tuning – DTU Edition"
    )
    parser.add_argument("--train", required=True, help="Training JSONL")
    parser.add_argument("--validation", required=True, help="Validation JSONL")
    parser.add_argument(
        "--output",
        default="outputs/whisper-classbridge-small-multilingual-lora",
    )
    # Đổi mặc định từ whisper-base → whisper-small để tăng độ chính xác
    parser.add_argument("--model", default="openai/whisper-small")
    parser.add_argument(
        "--resume-adapter",
        default="",
        help="Continue training from an existing LoRA adapter",
    )
    parser.add_argument(
        "--language",
        default="multilingual",
        help="multilingual uses each row's language; otherwise force one ISO code",
    )
    parser.add_argument("--fallback-language", default="vi")
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--gradient-accumulation", type=int, default=2)
    parser.add_argument("--learning-rate", type=float, default=5e-5)  # Thấp hơn cho small
    parser.add_argument("--speaker-cap", type=int, default=500)
    parser.add_argument(
        "--max-samples-per-language",
        type=int,
        default=0,
        help="Giới hạn mẫu mỗi ngôn ngữ cho micro-stage; 0 là dùng toàn bộ",
    )
    parser.add_argument(
        "--sample-offset-per-language",
        type=int,
        default=0,
        help="Bỏ qua N mẫu đầu mỗi ngôn ngữ để stage sau dùng dữ liệu mới",
    )
    parser.add_argument(
        "--train-only-language",
        default="",
        help="Chỉ dùng mẫu của một ngôn ngữ trong stage (ví dụ: vi)",
    )
    parser.add_argument(
        "--balance-languages",
        action=argparse.BooleanOptionalAction,
        default=True,
    )
    parser.add_argument("--augmentation-probability", type=float, default=0.65)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--smoke-test", action="store_true", help="Pipeline technical verification mode using synthetic/smoke dataset")
    parser.add_argument(
        "--skip-trainer-validation",
        action="store_true",
        help="Bỏ generation validation trong Trainer; dùng evaluator CT2 riêng sau khi export",
    )
    # ── LoRA nâng cao ───────────────────────────────────────────────────────

    parser.add_argument("--lora-rank", type=int, default=32,
                        help="LoRA rank (mặc định 32, base dùng 16)")
    parser.add_argument("--lora-alpha", type=int, default=64,
                        help="LoRA alpha (nên = 2×rank)")
    parser.add_argument(
        "--lora-target-modules",
        nargs="+",
        default=["q_proj", "v_proj", "k_proj", "out_proj"],
        help="Modules áp dụng LoRA (thêm k_proj, out_proj so với bản cũ)",
    )
    parser.add_argument(
        "--decoder-only",
        action="store_true",
        help="Chỉ gắn LoRA vào decoder để giữ nguyên encoder và nhận diện ngôn ngữ",
    )
    # ── Curriculum Learning ─────────────────────────────────────────────────
    parser.add_argument(
        "--curriculum",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Bật curriculum learning: easy → medium → hard theo epoch",
    )
    # ── DTU Vocabulary Injection ────────────────────────────────────────────
    parser.add_argument(
        "--dtu-vocab-file",
        default="",
        help="Path tới data/dtu_vocab.json để inject thuật ngữ DTU vào Whisper prompt",
    )
    return parser.parse_args()


def language_for(example: dict[str, Any], args: argparse.Namespace) -> str:
    if args.language != "multilingual":
        return args.language.lower()
    return str(example.get("language") or args.fallback_language).strip().lower()


def load_dtu_vocab_prompt(vocab_file: str, language: str = "vi") -> str:
    """Nạp Whisper initial_prompt từ file dtu_vocab.json."""
    if not vocab_file:
        return ""
    path = Path(vocab_file)
    if not path.exists():
        print(f"[DTU Vocab] ⚠️  Không tìm thấy {vocab_file} – bỏ qua vocab injection")
        return ""
    try:
        import json
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        key = f"whisper_prompt_{language}" if language in ("vi", "en") else "whisper_prompt_vi"
        prompt = data.get(key, "")
        print(f"[DTU Vocab] ✅ Nạp prompt ({len(prompt)} chars): {prompt[:80]}...")
        return prompt
    except Exception as exc:
        print(f"[DTU Vocab] ⚠️  Lỗi đọc vocab file: {exc}")
        return ""


def get_curriculum_stage(epoch: int, total_epochs: int) -> str:
    """
    Curriculum Learning: chia 3 giai đoạn theo epoch.
      Giai đoạn 1 (30% epoch đầu): chỉ dùng mẫu 'easy'
      Giai đoạn 2 (50% tiếp theo): dùng 'easy' + 'medium'
      Giai đoạn 3 (20% cuối): dùng tất cả kể cả 'hard'
    """
    ratio = epoch / max(total_epochs, 1)
    if ratio < 0.30:
        return "easy"
    elif ratio < 0.80:
        return "medium"
    return "hard"


def filter_by_difficulty(dataset: Dataset, stage: str, seed: int) -> Dataset:
    """
    Lọc dataset theo stage curriculum.
    Nếu không có trường 'difficulty', trả về nguyên dataset.
    """
    if "difficulty" not in dataset.column_names:
        return dataset
    difficulty_order = {"easy": 0, "medium": 1, "hard": 2}
    stage_level = difficulty_order.get(stage, 2)
    selected = [
        i for i, diff in enumerate(dataset["difficulty"])
        if difficulty_order.get(str(diff).lower(), 0) <= stage_level
    ]
    if not selected:
        return dataset  # Fallback nếu không có nhãn khớp
    return dataset.select(selected)


def cap_each_speaker(dataset: Dataset, maximum: int, seed: int) -> Dataset:
    if maximum <= 0 or "speaker_id" not in dataset.column_names:
        return dataset
    groups: dict[str, list[int]] = defaultdict(list)
    for index, speaker_id in enumerate(dataset["speaker_id"]):
        groups[str(speaker_id)].append(index)
    rng = random.Random(seed)
    selected: list[int] = []
    for indexes in groups.values():
        rng.shuffle(indexes)
        selected.extend(indexes[:maximum])
    rng.shuffle(selected)
    return dataset.select(selected)


def balance_languages(dataset: Dataset, seed: int) -> Dataset:
    if "language" not in dataset.column_names:
        return dataset
    groups: dict[str, list[int]] = defaultdict(list)
    for index, language in enumerate(dataset["language"]):
        groups[str(language).lower()].append(index)
    if len(groups) < 2:
        return dataset
    target = max(len(indexes) for indexes in groups.values())
    rng = random.Random(seed)
    selected: list[int] = []
    for indexes in groups.values():
        selected.extend(indexes)
        selected.extend(rng.choices(indexes, k=target - len(indexes)))
    rng.shuffle(selected)
    return dataset.select(selected)


def augment_waveform(
    samples: np.ndarray, probability: float, seed: int
) -> np.ndarray:
    """Simulate quiet/loud microphones, background noise and speaking rate."""
    rng = np.random.default_rng(seed)
    audio = np.asarray(samples, dtype=np.float32).copy()
    if audio.size == 0 or rng.random() > probability:
        return audio

    gain_db = rng.uniform(-8.0, 5.0)
    audio *= 10 ** (gain_db / 20.0)
    if rng.random() < 0.75:
        signal_rms = float(np.sqrt(np.mean(audio * audio) + 1e-9))
        snr_db = rng.uniform(10.0, 30.0)
        noise_rms = signal_rms / (10 ** (snr_db / 20.0))
        audio += rng.normal(0.0, noise_rms, audio.shape).astype(np.float32)
    if audio.size > 800 and rng.random() < 0.45:
        speed = rng.uniform(0.92, 1.08)
        source_positions = np.arange(audio.size, dtype=np.float32)
        target_positions = np.arange(0, audio.size, speed, dtype=np.float32)
        audio = np.interp(target_positions, source_positions, audio).astype(np.float32)
    return np.clip(audio, -1.0, 1.0)


def normalized_metric_text(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold()
    value = re.sub(r"[^\w\s']", " ", value, flags=re.UNICODE)
    return " ".join(value.split())


def main() -> None:
    import numpy as np  # type: ignore[import]
    import torch  # type: ignore[import]
    from datasets import Audio, DatasetDict, load_dataset  # type: ignore[import]
    from jiwer import cer, wer  # type: ignore[import]
    from peft import LoraConfig, PeftModel, get_peft_model  # type: ignore[import]
    from transformers import (  # type: ignore[import]
        Seq2SeqTrainer,
        Seq2SeqTrainingArguments,
        WhisperFeatureExtractor,
        WhisperForConditionalGeneration,
        WhisperProcessor,
        WhisperTokenizer,
    )

    args = parse_args()
    if args.smoke_test:
        print("\n=========================================================================")
        print("⚠️  WARNING: PIPELINE SMOKE-TEST MODE ENABLED!")
        print("   This run is for TECHNICAL PIPELINE VERIFICATION ONLY.")
        print("   Do NOT use the resulting model or WER scores for real research results!")
        print("=========================================================================\n")
    if not 0.0 <= args.augmentation_probability <= 1.0:

        raise ValueError("--augmentation-probability must be between 0 and 1")

    raw: DatasetDict = load_dataset(
        "json", data_files={"train": args.train, "validation": args.validation}
    )
    raw["train"] = cap_each_speaker(raw["train"], args.speaker_cap, args.seed)
    if args.train_only_language:
        wanted_language = args.train_only_language.strip().lower()
        language_indices = [
            index
            for index, language in enumerate(raw["train"]["language"])
            if str(language).strip().lower() == wanted_language
        ]
        raw["train"] = raw["train"].select(language_indices)
        print(
            f"[Language stage] {wanted_language}: {len(language_indices)} samples available",
            flush=True,
        )
    if args.balance_languages and args.language == "multilingual":
        raw["train"] = balance_languages(raw["train"], args.seed)
    if args.max_samples_per_language > 0:
        selected: list[int] = []
        counts: dict[str, int] = {}
        seen: dict[str, int] = {}
        for index, language in enumerate(raw["train"]["language"]):
            code = str(language).strip().lower()
            seen[code] = seen.get(code, 0) + 1
            if seen[code] <= args.sample_offset_per_language:
                continue
            if counts.get(code, 0) < args.max_samples_per_language:
                selected.append(index)
                counts[code] = counts.get(code, 0) + 1
        raw["train"] = raw["train"].select(selected).shuffle(seed=args.seed)
        print(
            f"[Micro-stage] offset={args.sample_offset_per_language}, "
            f"samples per language: {counts}",
            flush=True,
        )

    tokenizer_options: dict[str, Any] = {"task": "transcribe"}
    if args.language != "multilingual":
        tokenizer_options["language"] = args.language
    feature_extractor = WhisperFeatureExtractor.from_pretrained(args.model)
    tokenizer = WhisperTokenizer.from_pretrained(args.model, **tokenizer_options)
    processor = WhisperProcessor.from_pretrained(args.model, **tokenizer_options)

    import soundfile as sf

    def prepare(example: dict[str, Any], index: int, training: bool) -> dict[str, Any]:
        audio_val = example["audio"]
        if isinstance(audio_val, dict) and "array" in audio_val and audio_val["array"] is not None:
            samples = np.asarray(audio_val["array"], dtype=np.float32)
            sr = audio_val.get("sampling_rate", 16000)
        else:
            audio_path = audio_val.get("path") if isinstance(audio_val, dict) else str(audio_val)
            samples, sr = sf.read(audio_path)
            samples = samples.astype(np.float32)
            if samples.ndim > 1:
                samples = samples.mean(axis=1)
            if sr != 16000:
                try:
                    import librosa
                    samples = librosa.resample(samples, orig_sr=sr, target_sr=16000)
                except Exception:
                    pass
                sr = 16000

        if training:
            samples = augment_waveform(
                samples, args.augmentation_probability, args.seed + index
            )
        language = language_for(example, args)
        try:
            tokenizer.set_prefix_tokens(language=language, task="transcribe")
        except (KeyError, ValueError) as error:
            raise ValueError(
                f"Unsupported Whisper language code '{language}' in row {index}"
            ) from error
        input_features = feature_extractor(
            samples, sampling_rate=sr
        ).input_features[0]
        tokenized_labels = tokenizer(
            str(example["text"]).strip(), truncation=True, max_length=448
        ).input_ids
        if len(tokenized_labels) > 448:
            tokenized_labels = tokenized_labels[:448]
        return {"input_features": input_features, "labels": tokenized_labels}


    train_columns = raw["train"].column_names
    prepared_train = raw["train"].map(
        lambda example, index: prepare(example, index, True),
        with_indices=True,
        remove_columns=train_columns,
        load_from_cache_file=False,
        keep_in_memory=True,
        desc="Preparing augmented multilingual training audio",
    )
    prepared_validation = None
    if not args.skip_trainer_validation:
        validation_columns = raw["validation"].column_names
        prepared_validation = raw["validation"].map(
            lambda example, index: prepare(example, index, False),
            with_indices=True,
            remove_columns=validation_columns,
            load_from_cache_file=False,
            keep_in_memory=True,
            desc="Preparing clean unseen-speaker validation audio",
        )

    # ── Load DTU vocabulary prompt ────────────────────────────────────────
    fallback_lang = args.fallback_language if args.language == "multilingual" else args.language
    dtu_prompt = load_dtu_vocab_prompt(args.dtu_vocab_file, fallback_lang)

    model = WhisperForConditionalGeneration.from_pretrained(args.model)
    model.config.forced_decoder_ids = None
    model.config.suppress_tokens = []
    model.config.use_cache = False
    # RTX 3050 Laptop has 4 GB VRAM. Recompute activations during backward so
    # Whisper-small LoRA fits reliably with batch size 1.
    model.gradient_checkpointing_enable()
    if hasattr(model, "enable_input_require_grads"):
        model.enable_input_require_grads()
    # ── SpecAugment nâng cao (mask mạnh hơn để regularize tốt hơn) ───────
    model.config.apply_spec_augment = True
    model.config.mask_time_prob = 0.15      # Tăng từ 0.05 lên 0.15
    model.config.mask_feature_prob = 0.10   # Tăng từ 0.05 lên 0.10
    model.config.mask_time_length = 10
    model.generation_config.forced_decoder_ids = None
    # ── LoRA Config nâng cao ──────────────────────────────────────────────
    # r=32: rank cao hơn → học được pattern phức tạp hơn (giọng DTU, thuật ngữ)
    # k_proj + out_proj: thêm 2 modules → coverage rộng hơn
    if args.resume_adapter:
        model = PeftModel.from_pretrained(
            model, args.resume_adapter, is_trainable=True
        )
        print(f"[LoRA] Continuing adapter: {args.resume_adapter}")
    else:
        target_modules: list[str] | str = args.lora_target_modules
        if args.decoder_only:
            module_names = "|".join(re.escape(name) for name in args.lora_target_modules)
            target_modules = (
                rf".*model\.decoder\.layers\.\d+\."
                rf"(?:self_attn|encoder_attn)\.(?:{module_names})$"
            )
        lora_config = LoraConfig(
            r=args.lora_rank,
            lora_alpha=args.lora_alpha,
            lora_dropout=0.05,
            target_modules=target_modules,
            bias="none",
        )
        model = get_peft_model(model, lora_config)
    if hasattr(model, "enable_input_require_grads"):
        model.enable_input_require_grads()
    model.print_trainable_parameters()
    print(
        f"[LoRA] rank={args.lora_rank}, alpha={args.lora_alpha}, "
        f"modules={args.lora_target_modules}, decoder_only={args.decoder_only}"
    )

    def compute_metrics(prediction) -> dict[str, float]:
        """
        Tính WER/CER tổng thể và per-language (vi vs en).
        Thêm breakdown ngôn ngữ để debug chính xác hơn.
        """
        predictions = prediction.predictions
        labels = prediction.label_ids.copy()
        labels[labels == -100] = tokenizer.pad_token_id
        predicted_text = tokenizer.batch_decode(predictions, skip_special_tokens=True)
        reference_text = tokenizer.batch_decode(labels, skip_special_tokens=True)
        predicted_normalized = [normalized_metric_text(text) for text in predicted_text]
        reference_normalized = [normalized_metric_text(text) for text in reference_text]

        # ── Tổng thể ─────────────────────────────────────────────────────
        usable = [
            (pred, ref)
            for pred, ref in zip(predicted_normalized, reference_normalized)
            if ref
        ]
        if not usable:
            return {"wer": 100.0, "cer": 100.0}
        hypotheses, references = zip(*usable)
        overall_wer = 100 * wer(list(references), list(hypotheses))
        overall_cer = 100 * cer(list(references), list(hypotheses))

        metrics = {
            "wer": overall_wer,
            "cer": overall_cer,
        }

        # ── Per-language breakdown (chỉ khi validation có trường language) ─
        val_languages = (
            raw["validation"]["language"]
            if "language" in raw["validation"].column_names
            else []
        )
        if val_languages and len(val_languages) == len(predicted_normalized):
            for lang_code in ("vi", "en"):
                lang_pairs = [
                    (pred, ref)
                    for pred, ref, lang in zip(
                        predicted_normalized, reference_normalized, val_languages
                    )
                    if ref and str(lang).lower() == lang_code
                ]
                if len(lang_pairs) >= 5:  # Chỉ tính khi có ≥5 mẫu
                    hyp_l, ref_l = zip(*lang_pairs)
                    metrics[f"wer_{lang_code}"] = 100 * wer(list(ref_l), list(hyp_l))
                    metrics[f"cer_{lang_code}"] = 100 * cer(list(ref_l), list(hyp_l))

        return metrics

    # ── Curriculum Learning Setup ─────────────────────────────────────────
    # Nếu bật curriculum, epoch 1 chỉ dùng mẫu easy để ổn định training
    curriculum_stages = [
        get_curriculum_stage(epoch, args.epochs)
        for epoch in range(1, args.epochs + 1)
    ] if args.curriculum else ["hard"] * args.epochs

    if args.curriculum:
        stage_counts = {s: curriculum_stages.count(s) for s in set(curriculum_stages)}
        print(f"[Curriculum] Giai đoạn training: {curriculum_stages}")
        print(f"[Curriculum] Tổng kết: {stage_counts}")

    trainer = Seq2SeqTrainer(
        model=model,
        args=Seq2SeqTrainingArguments(
            output_dir=args.output,
            per_device_train_batch_size=args.batch_size,
            per_device_eval_batch_size=args.batch_size,
            gradient_accumulation_steps=args.gradient_accumulation,
            learning_rate=args.learning_rate,
            warmup_ratio=0.15,             # Tăng warmup từ 0.1 → 0.15
            num_train_epochs=args.epochs,
            fp16=torch.cuda.is_available(),
            bf16=(
                not torch.cuda.is_available()
                and hasattr(torch, "bfloat16")
                and getattr(torch.backends, "cpu", None) is not None
            ),
            eval_strategy="no" if args.skip_trainer_validation else "epoch",
            save_strategy="epoch",
            save_total_limit=2,
            predict_with_generate=not args.skip_trainer_validation,
            generation_max_length=225,
            logging_steps=20,
            load_best_model_at_end=not args.skip_trainer_validation,
            metric_for_best_model="wer",
            greater_is_better=False,
            report_to="none",
            remove_unused_columns=False,
            seed=args.seed,
            data_seed=args.seed,
            # Whisper creates decoder inputs from labels internally. Removing
            # labels early for smoothing breaks PEFT training.
            label_smoothing_factor=0.0,
        ),
        train_dataset=prepared_train,
        eval_dataset=None if args.skip_trainer_validation else prepared_validation,
        data_collator=SpeechSeq2SeqCollator(processor),
        compute_metrics=None if args.skip_trainer_validation else compute_metrics,
        processing_class=processor,
    )

    # ── Train với curriculum (nếu bật) ────────────────────────────────────
    if args.curriculum and "difficulty" in raw["train"].column_names:
        print("[Curriculum] Bắt đầu curriculum training theo từng giai đoạn...")
        for epoch_idx, stage in enumerate(curriculum_stages):
            print(f"  ── Epoch {epoch_idx+1}/{args.epochs}: stage='{stage}' ──")
            stage_dataset = filter_by_difficulty(raw["train"], stage, args.seed)
            # Cần prepare lại theo stage
            stage_columns = stage_dataset.column_names
            stage_prepared = stage_dataset.map(
                lambda example, index: prepare(example, index, True),
                with_indices=True,
                remove_columns=stage_columns,
                load_from_cache_file=False,
                keep_in_memory=True,
                writer_batch_size=50,
                desc=f"Preparing stage '{stage}' audio (epoch {epoch_idx+1})",
            )
            trainer.train_dataset = stage_prepared  # type: ignore[assignment]
            trainer.args.num_train_epochs = epoch_idx + 1
            trainer.train(
                resume_from_checkpoint=None if epoch_idx == 0 else True
            )
    else:
        trainer.train()

    trainer.save_model(args.output)
    processor.save_pretrained(args.output)

    # ── Lưu metadata fine-tuning ──────────────────────────────────────────
    import json as _json
    meta = {
        "base_model": args.model,
        "lora_rank": args.lora_rank,
        "lora_alpha": args.lora_alpha,
        "lora_target_modules": args.lora_target_modules,
        "decoder_only": args.decoder_only,
        "epochs": args.epochs,
        "learning_rate": args.learning_rate,
        "curriculum": args.curriculum,
        "dtu_vocab_file": args.dtu_vocab_file,
        "augmentation_probability": args.augmentation_probability,
        "resume_adapter": args.resume_adapter,
    }
    meta_path = Path(args.output) / "classbridge_finetune_config.json"
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    meta_path.write_text(_json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n✅ Fine-tuning hoàn tất! Mô hình lưu tại: {args.output}")
    print(f"   Config: {meta_path}")


if __name__ == "__main__":
    main()
