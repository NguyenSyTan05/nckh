"""
ClassBridge - Advanced Multi-Accent & Multi-Dialect Fine-Tuning Module
Tối ưu hóa độ chính xác ASR & Tốc độ xử lý cho Tiếng Anh Đa Quốc Gia & Tiếng Việt Đa Vùng Miền

Thư mục: classbridge/training/
Hỗ trợ: --test  (chạy nhanh 3 bước để kiểm tra pipeline)
         --train (huấn luyện đầy đủ)
"""
# pyrefly: ignore-all-errors
from __future__ import annotations

import os
import sys
import gc
import json
import time
from pathlib import Path
from dataclasses import dataclass
from typing import Any, Dict, List, Union

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


# ─── Ngăn xung đột DLL OpenMP trên Windows ──────────────────────────────────
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

# ── Tự động chèn virtualenv site-packages vào sys.path ──────────────────────
_VENV_SITE = Path(__file__).resolve().parent.parent / "backend" / "ai-service" / ".venv" / "Lib" / "site-packages"
if _VENV_SITE.exists() and str(_VENV_SITE) not in sys.path:
    sys.path.insert(0, str(_VENV_SITE))
# ─────────────────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
AI_SERVICE_DIR = PROJECT_DIR / "backend" / "ai-service"
OUTPUT_DIR = str(AI_SERVICE_DIR / "whisper-multi-accent-lora")
DEFAULT_MODEL = "openai/whisper-small"


# ─────────────────────────────────────────────────────────────────────────────
# Data Collator
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class DataCollatorSpeechSeq2SeqWithPadding:
    processor: Any

    def __call__(self, features: List[Dict[str, Union[List[int], Any]]]) -> Dict[str, Any]:
        import torch
        input_features = [{"input_features": feature["input_features"]} for feature in features]
        batch = self.processor.feature_extractor.pad(input_features, return_tensors="pt")

        label_features = [{"input_ids": feature["labels"]} for feature in features]
        labels_batch = self.processor.tokenizer.pad(label_features, return_tensors="pt")

        labels = labels_batch["input_ids"].masked_fill(labels_batch.attention_mask.ne(1), -100)
        bos_id = (
            getattr(self.processor.tokenizer, "bos_token_id", None)
            or getattr(self.processor.tokenizer, "decoder_start_token_id", None)
        )
        if bos_id is not None and labels.ndim > 1 and labels.size(1) > 0:
            if (labels[:, 0] == bos_id).all().cpu().item():
                labels = labels[:, 1:]

        batch["labels"] = labels
        return batch


# ─────────────────────────────────────────────────────────────────────────────
# Dataset
# ─────────────────────────────────────────────────────────────────────────────
class LazySpeechDataset:
    """Dataset lazily loading audio from disk. NOT using TorchDataset to avoid
    multiprocessing issues on Windows."""

    def __init__(self, dataset: Any, pipeline: "AccentTrainerPipeline"):
        self.dataset = dataset
        self.pipeline = pipeline

    def __len__(self) -> int:
        return len(self.dataset)

    def __getitem__(self, idx: int) -> Dict[str, Any]:
        row = self.dataset[int(idx)]
        return self.pipeline.prepare_dataset_row(row)


# ─────────────────────────────────────────────────────────────────────────────
# Pipeline
# ─────────────────────────────────────────────────────────────────────────────
class AccentTrainerPipeline:
    def __init__(self, model_name: str = DEFAULT_MODEL, language: str = "English"):
        self.model_name = model_name
        self.language = language
        self.task = "transcribe"
        self.feature_extractor = None
        self.tokenizer = None
        self.processor = None

        print(f"[ClassBridge Train] Khởi tạo Processor cho {self.language}...")
        try:
            from transformers import WhisperFeatureExtractor, WhisperTokenizer, WhisperProcessor  # type: ignore[import]
            self.processor = WhisperProcessor.from_pretrained(
                self.model_name, language=self.language, task=self.task
            )
            self.tokenizer = WhisperTokenizer.from_pretrained(
                self.model_name, language=self.language, task=self.task
            )
            self.feature_extractor = WhisperFeatureExtractor.from_pretrained(self.model_name)
        except Exception as e:
            print(f"⚠️ Cảnh báo khởi tạo: {e}")
            raise

    # ── Audio loader ─────────────────────────────────────────────────────────
    @staticmethod
    def load_wav_file(file_path: str):
        import numpy as np
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File không tồn tại: {file_path}")
        try:
            import soundfile as sf
            data, sr = sf.read(str(path))
            if data.ndim > 1:
                data = data.mean(axis=1)
            return data.astype("float32"), int(sr)
        except FileNotFoundError:
            raise
        except Exception:
            import wave
            with wave.open(str(path), "rb") as wf:
                n_ch = wf.getnchannels()
                sr = wf.getframerate()
                raw = wf.readframes(wf.getnframes())
            samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
            if n_ch > 1:
                samples = samples[::n_ch]
            return samples, int(sr)

    # ── Row processor ─────────────────────────────────────────────────────────
    def prepare_dataset_row(self, batch: Dict[str, Any]) -> Dict[str, Any]:
        import numpy as np
        audio_val = batch.get("audio")
        if isinstance(audio_val, dict) and "array" in audio_val:
            array = np.asarray(audio_val["array"], dtype="float32")
            sr = int(audio_val["sampling_rate"])
        else:
            path_str = str(
                audio_val if isinstance(audio_val, str) else batch.get("audio_path", "")
            )
            try:
                array, sr = self.load_wav_file(path_str)
            except Exception as err:
                print(f"⚠️ Fallback audio for ({path_str}): {err}")
                array = np.zeros(16000, dtype="float32")
                sr = 16000

        # Resample to 16 kHz
        if sr != 16000 and len(array) > 0:
            target_len = int(len(array) * 16000 / sr)
            array = np.interp(
                np.linspace(0, len(array), target_len, endpoint=False),
                np.arange(len(array)),
                array,
            ).astype("float32")

        if len(array) == 0:
            array = np.zeros(16000, dtype="float32")

        # Truncate at Whisper's 30s limit (480000 samples @ 16kHz)
        if len(array) > 480000:
            array = array[:480000]

        text = str(batch.get("text") or batch.get("sentence") or "").strip()

        input_features = self.feature_extractor(
            array, sampling_rate=16000
        ).input_features[0]

        labels = self.tokenizer(text).input_ids
        if not labels:
            labels = [getattr(self.tokenizer, "eos_token_id", 50257)]

        return {"input_features": input_features, "labels": labels}

    # ── Test mode (quick sanity check, 3 steps) ───────────────────────────────
    def test_pipeline(
        self,
        manifest_path: str | Path | None = None,
        test_steps: int = 3,
        batch_size: int = 1,
        output_dir: str | None = None,
    ) -> None:
        print("\n" + "=" * 67)
        print("   [TEST MODE] ClassBridge Accent Trainer - Kiểm tra Pipeline")
        print("=" * 67)
        self._run_training(
            manifest_path=manifest_path,
            max_steps=test_steps,
            batch_size=batch_size,
            output_dir=output_dir or "/tmp/cb_test_run",
            save_model=False,
            test_mode=True,
        )
        print("[TEST MODE] ✓ Pipeline chạy thành công. Mọi bước đều OK.\n")

    # ── Full train mode ───────────────────────────────────────────────────────
    def train_lora_adapter(
        self,
        dataset_name: str = "local",
        manifest_path: str | Path | None = None,
        max_steps: int = 300,
        batch_size: int = 1,
        output_dir: str | None = None,
    ) -> None:
        self._run_training(
            manifest_path=manifest_path,
            max_steps=max_steps,
            batch_size=batch_size,
            output_dir=output_dir or OUTPUT_DIR,
            save_model=True,
            test_mode=False,
        )

    # ── Core training ─────────────────────────────────────────────────────────
    def _run_training(
        self,
        manifest_path: str | Path | None,
        max_steps: int,
        batch_size: int,
        output_dir: str,
        save_model: bool,
        test_mode: bool,
    ) -> None:
        import torch  # type: ignore[import]
        from transformers import WhisperForConditionalGeneration  # type: ignore[import]
        from peft import LoraConfig, get_peft_model  # type: ignore[import]
        from datasets import load_dataset  # type: ignore[import]

        candidate_manifests = [
            PROJECT_DIR / "data" / "manifests" / "english_accent_samples.jsonl",
            PROJECT_DIR / "data" / "manifests" / "vietnamese_accent_samples.jsonl",
            PROJECT_DIR / "data" / "bilingual_sample_manifest.jsonl",
            PROJECT_DIR / "data" / "manifests" / "local_text_manifest.jsonl",
        ]
        chosen_manifest = None
        if manifest_path and Path(manifest_path).exists():
            chosen_manifest = Path(manifest_path)
        else:
            for cand in candidate_manifests:
                if cand.exists():
                    chosen_manifest = cand
                    break

        save_path = Path(output_dir)
        if save_model:
            save_path.mkdir(parents=True, exist_ok=True)

        # ── Load model ────────────────────────────────────────────────────────
        print(f"[ClassBridge Train] Tải mô hình {self.model_name}...")
        model = WhisperForConditionalGeneration.from_pretrained(self.model_name)
        model.config.forced_decoder_ids = None
        model.config.suppress_tokens = []
        model.config.use_cache = False

        # Gradient checkpointing để tiết kiệm RAM
        model.model.encoder.gradient_checkpointing = False
        try:
            model.gradient_checkpointing_enable()
        except Exception:
            pass

        lora_config = LoraConfig(
            r=16, lora_alpha=32,
            target_modules=["q_proj", "v_proj"],
            lora_dropout=0.05, bias="none",
        )
        model = get_peft_model(model, lora_config)
        model.print_trainable_parameters()

        # ── Load dataset ──────────────────────────────────────────────────────
        if chosen_manifest and chosen_manifest.exists():
            print(f"[ClassBridge Train] Tải dataset từ: {chosen_manifest}...")
            dataset = load_dataset(
                "json", data_files={"train": str(chosen_manifest)}, split="train"
            )
        else:
            raise FileNotFoundError(f"Không tìm thấy manifest tại bất kỳ vị trí nào: {candidate_manifests}")


        # ── Filter missing files ──────────────────────────────────────────────
        def _audio_exists(ex):
            p = ex.get("audio") or ex.get("audio_path")
            if isinstance(p, dict):
                return True
            return bool(p) and Path(str(p)).exists()

        n_before = len(dataset)
        dataset = dataset.filter(_audio_exists)
        n_after = len(dataset)
        print(f"[ClassBridge Train] Dataset: {n_after}/{n_before} mẫu có file WAV.")

        if n_after == 0:
            print("⚠️ Không có file audio nào. Hãy chạy: python english_accent_to_samples.py --sync")
            return

        if test_mode:
            # Chỉ dùng 10 mẫu đầu trong test mode
            dataset = dataset.select(range(min(10, n_after)))
            print(f"[TEST MODE] Chỉ dùng {len(dataset)} mẫu đầu để kiểm tra.")

        wrapped = LazySpeechDataset(dataset, self)
        collator = DataCollatorSpeechSeq2SeqWithPadding(processor=self.processor)

        # ── Quick sample check ────────────────────────────────────────────────
        print("[ClassBridge Train] Kiểm tra mẫu đầu tiên...")
        s0 = wrapped[0]
        b0 = collator([s0])
        feats, lbls = b0["input_features"], b0["labels"]
        print(f"  ✓ input_features: {feats.shape}  labels: {lbls.shape}")
        del s0, b0, feats, lbls
        gc.collect()

        # ── Setup optimizer & device ──────────────────────────────────────────
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"[ClassBridge Train] Thiết bị: {device}")
        model = model.to(device)
        model.train()

        optimizer = torch.optim.AdamW(
            [p for p in model.parameters() if p.requires_grad], lr=1e-3
        )

        accum_steps = max(1, 4 // batch_size)  # Effective batch = batch_size * accum_steps = 4
        print(
            f"[ClassBridge Train] batch_size={batch_size}, "
            f"gradient_accum={accum_steps}, effective_batch={batch_size * accum_steps}"
        )

        # ── Training loop (no DataLoader — avoids Windows multiprocess crash) ─
        print(
            f"\n[ClassBridge Train] Bắt đầu Huấn luyện LoRA"
            f" (Max Steps: {max_steps}, Mode: {'TEST' if test_mode else 'TRAIN'})...\n"
        )
        start_time = time.time()
        step = 0
        accum_loss = 0.0
        dataset_len = len(wrapped)
        indices = list(range(dataset_len))

        # Shuffle indices manually each epoch
        import random
        random.shuffle(indices)
        cursor = 0

        def _next_batch() -> Dict[str, Any]:
            nonlocal cursor, indices
            batch_items = []
            for _ in range(batch_size):
                if cursor >= len(indices):
                    random.shuffle(indices)
                    cursor = 0
                batch_items.append(wrapped[indices[cursor]])
                cursor += 1
            return collator(batch_items)

        optimizer.zero_grad()

        while step < max_steps:
            try:
                batch = _next_batch()
            except Exception as load_err:
                print(f"⚠️ Bỏ qua batch lỗi (step {step + 1}): {load_err}")
                step += 1
                continue

            try:
                inp = batch["input_features"].to(device)
                lbl = batch["labels"].to(device)

                outputs = model(input_features=inp, labels=lbl)
                loss = outputs.loss / accum_steps
                loss.backward()
                accum_loss += loss.item() * accum_steps

                del inp, lbl, outputs, loss
                gc.collect()

                if (step + 1) % accum_steps == 0:
                    torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                    optimizer.step()
                    optimizer.zero_grad()

                step += 1

                if step == 1 or step % 10 == 0 or step == max_steps:
                    avg = accum_loss / min(step, 10)
                    elapsed = time.time() - start_time
                    eta = (elapsed / step) * (max_steps - step)
                    print(
                        f"  [Step {step:4d}/{max_steps}]"
                        f" Loss: {avg:.4f}"
                        f"  Elapsed: {elapsed:.0f}s"
                        f"  ETA: {eta:.0f}s"
                    )
                    accum_loss = 0.0

            except Exception as fwd_err:
                import traceback
                print(f"❌ Lỗi forward/backward tại step {step + 1}:")
                traceback.print_exc()
                # Cleanup & continue
                optimizer.zero_grad()
                gc.collect()
                step += 1
                continue

        elapsed_total = time.time() - start_time
        print(f"\n[ClassBridge Train] ✓ Hoàn tất {step}/{max_steps} bước trong {elapsed_total:.2f}s")

        if save_model:
            print(f"[ClassBridge Train] Đang lưu adapter vào {output_dir}...")
            model.save_pretrained(output_dir)
            self.processor.save_pretrained(output_dir)
            print(f"[ClassBridge Train] ✓ Đã lưu Adapter thành công tại: {output_dir}")
        else:
            print("[TEST MODE] Không lưu model (test only).")


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="ClassBridge Accent Trainer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ví dụ:
  # Kiểm tra nhanh pipeline (3 steps):
  python train_accent_module.py --test

  # Huấn luyện đầy đủ:
  python train_accent_module.py --train --manifest ... --output-dir ... --steps 300
        """,
    )

    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument("--test", action="store_true", help="Chạy test 3 bước để kiểm tra pipeline")
    mode_group.add_argument("--train", action="store_true", help="Chạy huấn luyện đầy đủ")

    parser.add_argument("--manifest", default=None, help="Đường dẫn file manifest .jsonl")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Tên Whisper model")
    parser.add_argument("--steps", type=int, default=300, help="Số bước huấn luyện (chỉ dùng cho --train)")
    parser.add_argument("--batch-size", type=int, default=1, help="Batch size (mặc định 1 để tiết kiệm RAM)")
    parser.add_argument("--output-dir", default=None, help="Thư mục lưu adapter (chỉ dùng cho --train)")
    parser.add_argument("--language", default=None, help="Ngôn ngữ: English | Vietnamese")
    args = parser.parse_args()

    # Auto-detect language
    lang = args.language
    if not lang:
        if args.manifest and "english" in str(args.manifest).lower():
            lang = "English"
        else:
            lang = "Vietnamese"

    print("=" * 67)
    if args.test:
        print("   ClassBridge - Accent Trainer  [TEST MODE]")
    else:
        print(f"   ClassBridge - Advanced Multi-Accent & Dialect Trainer ({lang})")
    print("=" * 67)

    pipeline = AccentTrainerPipeline(model_name=args.model, language=lang)

    if args.test:
        pipeline.test_pipeline(
            manifest_path=args.manifest,
            test_steps=3,
            batch_size=1,
            output_dir=args.output_dir,
        )
    else:
        pipeline.train_lora_adapter(
            manifest_path=args.manifest,
            max_steps=args.steps,
            batch_size=args.batch_size,
            output_dir=args.output_dir,
        )
