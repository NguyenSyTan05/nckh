"""
ClassBridge - Advanced Neural Translation Fine-Tuning Module (NMT Training)
Tăng tỷ lệ chính xác phiên dịch 2 chiều Anh ↔ Việt cho bài giảng học thuật

Thư mục: classbridge/training/

Chức năng chính:
  - Fine-tune VietAI/envit5-translation với LoRA (PEFT)
  - Hỗ trợ dịch 2 chiều: EN→VI và VI→EN (tự động prefix "en:" / "vi:")
  - Load dataset từ file JSONL ngoài hoặc bộ mẫu nội bộ 20 câu
  - Đánh giá BLEU score sau mỗi epoch (sacrebleu)
  - TaskType.SEQ_2_SEQ_LM cho encoder-decoder đúng chuẩn

Format JSONL (2 schema đều được hỗ trợ):
  Schema A (manifest): {"en": "The neural network ...", "vi": "Mạng thần kinh ..."}
  Schema B (training):  {"source": "...", "target": "...", "direction": "en2vi"|"vi2en"}
  Trường "direction" không bắt buộc (mặc định "en2vi").
"""
# pyrefly: ignore-all-errors
from __future__ import annotations

import sys
import re
import json
import time
import unicodedata
from pathlib import Path
from typing import Dict, List, Optional, Union

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ── Tự động chèn virtualenv site-packages vào sys.path ──────────────────────
_VENV_SITE = Path(__file__).resolve().parent.parent / "backend" / "ai-service" / ".venv" / "Lib" / "site-packages"
if _VENV_SITE.exists() and str(_VENV_SITE) not in sys.path:
    sys.path.insert(0, str(_VENV_SITE))
# ─────────────────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
AI_SERVICE_DIR = PROJECT_DIR / "backend" / "ai-service"
OUTPUT_DIR_TRANSLATION = str(AI_SERVICE_DIR / "nmt-academic-lora")

BASE_MODEL_EN_VI = "VietAI/envit5-translation"

# ── Bộ dữ liệu mẫu nội bộ (20 cặp EN↔VI học thuật) ─────────────────────────
BUILTIN_SAMPLES: List[Dict[str, str]] = [
    # EN → VI (prefix "en:")
    {"source": "en: Welcome to today's lecture on artificial intelligence.", "target": "Chào mừng các bạn đến với bài giảng hôm nay về trí tuệ nhân tạo."},
    {"source": "en: Please submit your assignment before next Monday.", "target": "Vui lòng nộp bài tập của bạn trước thứ Hai tuần sau."},
    {"source": "en: The neural network consists of multiple hidden layers.", "target": "Mạng thần kinh bao gồm nhiều lớp ẩn."},
    {"source": "en: This course carries three academic credits.", "target": "Khóa học này bao gồm ba tín chỉ học thuật."},
    {"source": "en: Do you have any questions regarding the midterm exam?", "target": "Các bạn có câu hỏi nào về bài thi giữa kỳ không?"},
    {"source": "en: The prerequisite for this course is Introduction to Programming.", "target": "Môn học tiên quyết cho khóa này là Nhập môn Lập trình."},
    {"source": "en: Deep learning has revolutionized computer vision tasks.", "target": "Học máy sâu đã tạo ra cuộc cách mạng trong các tác vụ thị giác máy tính."},
    {"source": "en: Machine learning models require large amounts of training data.", "target": "Các mô hình học máy cần lượng lớn dữ liệu huấn luyện."},
    {"source": "en: Natural language processing is a subfield of artificial intelligence.", "target": "Xử lý ngôn ngữ tự nhiên là một nhánh của trí tuệ nhân tạo."},
    {"source": "en: The final exam will cover all chapters from the syllabus.", "target": "Bài thi cuối kỳ sẽ bao gồm tất cả các chương trong đề cương môn học."},
    {"source": "en: Students must attend at least 80% of lectures.", "target": "Sinh viên phải tham dự ít nhất 80% số buổi bài giảng."},
    {"source": "en: Distributed systems coordinate multiple computers to work together.", "target": "Hệ thống phân tán điều phối nhiều máy tính hoạt động cùng nhau."},
    {"source": "en: The algorithm runs in O(n log n) time complexity.", "target": "Thuật toán chạy với độ phức tạp thời gian O(n log n)."},
    {"source": "en: Data structures such as trees and graphs are fundamental in CS.", "target": "Cấu trúc dữ liệu như cây và đồ thị là nền tảng trong khoa học máy tính."},
    {"source": "en: Software engineering principles ensure code maintainability.", "target": "Các nguyên tắc kỹ thuật phần mềm đảm bảo khả năng bảo trì mã nguồn."},
    # VI → EN (prefix "vi:")
    {"source": "vi: Chào mừng đến với bài giảng về học máy sâu.", "target": "Welcome to the lecture on deep learning."},
    {"source": "vi: Vui lòng nộp bài tập trước hạn chót.", "target": "Please submit your assignment before the deadline."},
    {"source": "vi: Mạng thần kinh nhân tạo bắt chước não người.", "target": "Artificial neural networks mimic the human brain."},
    {"source": "vi: Kỳ thi giữa kỳ sẽ diễn ra vào tuần tới.", "target": "The midterm exam will take place next week."},
    {"source": "vi: Môn học này yêu cầu kiến thức về cơ sở dữ liệu.", "target": "This course requires knowledge of databases."},
]


def _nfc(text: str) -> str:
    """Chuẩn hóa Unicode NFC để tránh mất dấu tiếng Việt."""
    return unicodedata.normalize("NFC", text)


def load_jsonl_dataset(
    jsonl_path: str,
    strict: bool = False,
    return_stats: bool = False,
) -> Union[List[Dict[str, str]], tuple]:
    """
    Load dataset từ file JSONL.

    Hỗ trợ 2 schema:
      Schema A (manifest): {"en": "...", "vi": "..."}
      Schema B (training):  {"source": "...", "target": "...", "direction": "en2vi"|"vi2en"}

    Tự động:
      - Detect schema từ field name.
      - Thêm prefix "en: " / "vi: " vào source nếu chưa có.
      - Chuẩn hóa Unicode NFC cho cả source và target.
      - Trim whitespace.
      - Theo dõi stats đầy đủ (total, loaded, skipped, duplicates, errors).
      - Duplicate chỉ cảnh báo, KHÔNG xóa.
      - Không âm thầm bỏ qua lỗi.
    """
    rows: List[Dict[str, str]] = []
    seen: Dict[str, int] = {}
    total = loaded = skipped = duplicates = errors = 0
    error_lines: List[str] = []
    path = Path(jsonl_path)
    if not path.exists():
        print(f"⚠️ Không tìm thấy file: {jsonl_path}")
        if return_stats:
            return rows, {"total": 0, "loaded": 0, "skipped": 0, "duplicates": 0, "errors": 0}
        return rows
    with open(path, encoding="utf-8") as f:
        for line_no, raw_line in enumerate(f, 1):
            line = raw_line.strip()
            total += 1
            if not line or line.startswith("#"):
                skipped += 1
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as err:
                msg = f"⚠️ Dòng {line_no}: JSON không hợp lệ – {err}"
                error_lines.append(msg)
                print(msg)
                errors += 1
                skipped += 1
                if strict:
                    raise ValueError(msg)
                continue

            # ── Detect schema: "en"/"vi" (Schema A) vs "source"/"target" (Schema B) ──
            if "en" in obj and "vi" in obj:
                # Schema A – manifest format
                source_raw = _nfc(str(obj["en"]).strip())
                target_raw = _nfc(str(obj["vi"]).strip())
                direction = str(obj.get("direction", "en2vi")).lower()
            else:
                # Schema B – training format
                source_raw = _nfc(str(obj.get("source") or obj.get("src") or "").strip())
                target_raw = _nfc(str(obj.get("target") or obj.get("tgt") or "").strip())
                direction = str(obj.get("direction", "en2vi")).lower()

            if not source_raw or not target_raw:
                msg = f"⚠️ Dòng {line_no}: thiếu source/target (rỗng)"
                error_lines.append(msg)
                print(msg + ", bỏ qua.")
                skipped += 1
                errors += 1
                if strict:
                    raise ValueError(msg)
                continue

            # ── Thêm language prefix sau khi strip + NFC ──────────────────────
            src_lower = source_raw.lower()
            if direction == "vi2en":
                source = source_raw if src_lower.startswith("vi:") else f"vi: {source_raw}"
            else:  # en2vi (default)
                source = source_raw if src_lower.startswith("en:") else f"en: {source_raw}"
            target = target_raw

            # ── Duplicate detection (cảnh báo, KHÔNG xóa) ────────────────────
            dedup_key = source_raw
            if dedup_key in seen:
                duplicates += 1
                print(f"⚠️ Duplicate dòng {line_no} (lần đầu dòng {seen[dedup_key]}): {source_raw[:60]}")
            else:
                seen[dedup_key] = line_no

            rows.append({"source": source, "target": target})
            loaded += 1

    print(f"[ClassBridge NMT] Đã nạp {len(rows)} mẫu từ {path.name}")
    print(f"📊 Stats – total: {total}, loaded: {loaded}, skipped: {skipped}, duplicates: {duplicates}, errors: {errors}")
    if error_lines:
        print(f"  Chi tiết lỗi ({len(error_lines)} dòng):")
        for e in error_lines[:10]:
            print(f"    {e}")
        if len(error_lines) > 10:
            print(f"    ... và {len(error_lines) - 10} lỗi khác")
    stats = {"total": total, "loaded": loaded, "skipped": skipped, "duplicates": duplicates, "errors": errors}
    if return_stats:
        return rows, stats
    return rows

class TranslationTrainerPipeline:
    def __init__(self, model_name: str = BASE_MODEL_EN_VI) -> None:
        self.model_name = model_name
        self.tokenizer = None
        print(f"[ClassBridge NMT] Khởi tạo Tokenizer cho {self.model_name}...")
        try:
            from transformers import AutoTokenizer  # type: ignore[import]
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            print(f"  ✅ Tokenizer sẵn sàng (vocab_size={self.tokenizer.vocab_size})")
        except Exception as e:
            print(f"⚠️ Cảnh báo khởi tạo Tokenizer: {e}")
            print("  Mẹo: pip install transformers sentencepiece")

    def preprocess_function(self, examples: Dict) -> Dict:
        """
        Tokenize batch gồm cả source (input) và target (labels).
        ✅ FIX: Dùng text_target= thay thế as_target_tokenizer() đã deprecated (transformers>=4.26).
        """
        assert self.tokenizer is not None, "Tokenizer chưa được khởi tạo!"
        model_inputs = self.tokenizer(
            examples["source"],
            max_length=256,
            truncation=True,
            padding="max_length",
        )
        # ✅ text_target= là cách đúng, as_target_tokenizer() đã bị xóa
        labels = self.tokenizer(
            text_target=examples["target"],
            max_length=256,
            truncation=True,
            padding="max_length",
        )
        # Đặt padding token thành -100 để loss không tính trên pad
        pad_id = self.tokenizer.pad_token_id
        model_inputs["labels"] = [
            [(t if t != pad_id else -100) for t in ids]
            for ids in labels["input_ids"]
        ]
        return model_inputs

    def compute_bleu(self, eval_pred) -> Dict[str, float]:
        """Tính BLEU score trên tập validation sau mỗi epoch."""
        try:
            import numpy as np
            from sacrebleu.metrics import BLEU  # type: ignore[import]
            assert self.tokenizer is not None
            predictions, label_ids = eval_pred
            if hasattr(predictions, "shape") and len(predictions.shape) == 3:
                predictions = np.argmax(predictions, axis=-1)
            label_ids = np.where(label_ids != -100, label_ids, self.tokenizer.pad_token_id)
            decoded_preds = self.tokenizer.batch_decode(predictions, skip_special_tokens=True)
            decoded_labels = self.tokenizer.batch_decode(label_ids, skip_special_tokens=True)
            decoded_preds = [p.strip() for p in decoded_preds]
            decoded_labels = [[r.strip()] for r in decoded_labels]
            bleu = BLEU(effective_order=True)
            score = bleu.corpus_score(decoded_preds, decoded_labels).score
            return {"bleu": round(score, 2)}
        except Exception as e:
            print(f"⚠️ Không tính được BLEU: {e}")
            return {"bleu": 0.0}

    def train_translation_lora(
        self,
        dataset_path: Optional[str] = None,
        epochs: int = 3,
        batch_size: int = 4,
        learning_rate: float = 5e-5,
        lora_rank: int = 16,
    ) -> None:
        """
        Fine-tune mô hình dịch thuật với LoRA.

        Args:
            dataset_path:  Path file JSONL (None → dùng bộ mẫu nội bộ 20 câu EN↔VI)
            epochs:        Số epochs (mặc định 3)
            batch_size:    Batch size per device (mặc định 4)
            learning_rate: Learning rate (mặc định 5e-5, phù hợp LoRA)
            lora_rank:     LoRA rank r (mặc định 16)
        """
        print(f"[ClassBridge NMT] Tải mô hình: {self.model_name}...")
        try:
            import torch  # type: ignore[import]
            from transformers import (  # type: ignore[import]
                AutoModelForSeq2SeqLM,
                Seq2SeqTrainingArguments,
                Seq2SeqTrainer,
                DataCollatorForSeq2Seq,
            )
            from peft import LoraConfig, get_peft_model, TaskType  # type: ignore[import]
            from datasets import Dataset  # type: ignore[import]

            assert self.tokenizer is not None, "Tokenizer chưa khởi tạo!"

            # ── Load dataset ─────────────────────────────────────────────────
            if dataset_path:
                p = Path(dataset_path)
                if not p.exists():
                    raise FileNotFoundError(
                        f"❌ Dataset không tồn tại: {dataset_path}\n"
                        f"   Kiểm tra lại đường dẫn hoặc bỏ --dataset để dùng bộ mẫu nội bộ."
                    )
                rows = load_jsonl_dataset(dataset_path)
                if not rows:
                    raise ValueError(
                        f"❌ Dataset rỗng (0 records): {dataset_path}\n"
                        f"   Không fallback tự động — kiểm tra format JSONL và field 'en'/'vi' hoặc 'source'/'target'."
                    )
                print(f"✅ Dataset: {p.name} ({len(rows)} records)")
            else:
                # Chế độ demo rõ ràng — không truyền --dataset
                print("[ClassBridge NMT] Không có --dataset → dùng bộ mẫu nội bộ (20 cặp EN↔VI).")
                print("⚠️  Đây là chế độ DEMO. Để train thực tế hãy dùng --dataset <path>.")
                rows = BUILTIN_SAMPLES

            print(f"[ClassBridge NMT] Tổng mẫu: {len(rows)}")

            # Train/eval split 80/20
            n_eval = max(1, len(rows) // 5)
            train_rows = rows[:-n_eval]
            eval_rows  = rows[-n_eval:]
            train_dataset = Dataset.from_list(train_rows)
            eval_dataset  = Dataset.from_list(eval_rows)
            print(f"  ➜ Train: {len(train_dataset)} | Eval: {len(eval_dataset)}")

            # ── Tokenize ──────────────────────────────────────────────────────
            train_processed = train_dataset.map(
                self.preprocess_function, batched=True,
                remove_columns=train_dataset.column_names,
                desc="Tokenizing train",
            )
            eval_processed = eval_dataset.map(
                self.preprocess_function, batched=True,
                remove_columns=eval_dataset.column_names,
                desc="Tokenizing eval",
            )

            # ── Model + LoRA ──────────────────────────────────────────────────
            model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)

            # ✅ task_type=SEQ_2_SEQ_LM bắt buộc cho encoder-decoder (T5/mT5/envit5)
            lora_config = LoraConfig(
                task_type=TaskType.SEQ_2_SEQ_LM,
                r=lora_rank,
                lora_alpha=lora_rank * 2,
                target_modules=["q", "v"],
                lora_dropout=0.05,
                bias="none",
            )
            model = get_peft_model(model, lora_config)
            model.print_trainable_parameters()

            # ── DataCollator ──────────────────────────────────────────────────
            data_collator = DataCollatorForSeq2Seq(
                self.tokenizer, model=model, padding=True, label_pad_token_id=-100
            )

            # ── Training arguments ────────────────────────────────────────────
            training_args = Seq2SeqTrainingArguments(
                output_dir=OUTPUT_DIR_TRANSLATION,
                per_device_train_batch_size=batch_size,
                per_device_eval_batch_size=batch_size,
                gradient_accumulation_steps=2,
                learning_rate=learning_rate,       # ✅ 5e-5 (sửa từ 5e-4 quá cao)
                warmup_ratio=0.1,
                num_train_epochs=epochs,
                fp16=torch.cuda.is_available(),
                eval_strategy="epoch",
                save_strategy="epoch",
                save_total_limit=2,
                predict_with_generate=True,
                generation_max_length=256,
                logging_steps=5,
                load_best_model_at_end=True,
                metric_for_best_model="bleu",
                greater_is_better=True,
                report_to="none",
                remove_unused_columns=False,
                label_smoothing_factor=0.1,
            )

            trainer = Seq2SeqTrainer(
                model=model,
                args=training_args,
                train_dataset=train_processed,
                eval_dataset=eval_processed,
                data_collator=data_collator,
                processing_class=self.tokenizer,
                compute_metrics=self.compute_bleu,
            )

            # ── Train ─────────────────────────────────────────────────────────
            print(f"\n[ClassBridge NMT] Bắt đầu Fine-Tuning mô hình Dịch thuật...")
            print(f"  Model   : {self.model_name}")
            print(f"  LoRA    : r={lora_rank}, alpha={lora_rank * 2}")
            print(f"  Epochs  : {epochs}  |  LR: {learning_rate}")
            print(f"  Output  : {OUTPUT_DIR_TRANSLATION}\n")

            start_time = time.time()
            trainer.train()
            elapsed = time.time() - start_time

            print(f"\n[ClassBridge NMT] ✅ Hoàn tất sau {elapsed:.1f}s ({elapsed/60:.1f} phút)!")

            # ── Lưu model + metadata ──────────────────────────────────────────
            model.save_pretrained(OUTPUT_DIR_TRANSLATION)
            self.tokenizer.save_pretrained(OUTPUT_DIR_TRANSLATION)

            meta = {
                "base_model": self.model_name,
                "lora_rank": lora_rank,
                "lora_alpha": lora_rank * 2,
                "epochs": epochs,
                "learning_rate": learning_rate,
                "train_samples": len(train_rows),
                "dataset_path": dataset_path or "builtin",
            }
            meta_path = Path(OUTPUT_DIR_TRANSLATION) / "classbridge_nmt_config.json"
            meta_path.parent.mkdir(parents=True, exist_ok=True)
            meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")

            print(f"[ClassBridge NMT] Mô hình đã lưu tại: {OUTPUT_DIR_TRANSLATION}")
            print(f"[ClassBridge NMT] Config: {meta_path}")

        except ImportError as e:
            print(f"❌ Thiếu thư viện: {e}")
            print("  Chạy: pip install torch transformers peft datasets sacrebleu sentencepiece")
        except AssertionError as e:
            print(f"❌ Lỗi tiền điều kiện: {e}")
        except Exception as e:
            import traceback
            print(f"❌ Lỗi huấn luyện: {e}")
            traceback.print_exc()
            print("\n  Mẹo debug:")
            print("  - Kiểm tra kết nối internet (lần đầu cần tải model ~300MB)")
            print("  - Thử: pip install -U transformers peft datasets sacrebleu")


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="ClassBridge - Academic NMT Fine-Tuner (EN↔VI)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ví dụ:
  # Dùng bộ mẫu nội bộ (20 cặp EN↔VI):
  python train_translation_module.py

  # Dùng file JSONL tùy chỉnh:
  python train_translation_module.py --dataset data/my_pairs.jsonl

  # Tùy chỉnh đầy đủ:
  python train_translation_module.py --dataset my.jsonl --epochs 5 --lr 3e-5 --batch-size 8
        """,
    )
    parser.add_argument("--dataset", default=None, help="File JSONL {source, target, direction}")
    parser.add_argument("--model", default=BASE_MODEL_EN_VI, help="Tên model HuggingFace")
    parser.add_argument("--epochs", type=int, default=3, help="Số epochs (mặc định 3)")
    parser.add_argument("--batch-size", type=int, default=4, help="Batch size (mặc định 4)")
    parser.add_argument("--lr", type=float, default=5e-5, help="Learning rate (mặc định 5e-5)")
    parser.add_argument("--lora-rank", type=int, default=16, help="LoRA rank (mặc định 16)")
    args = parser.parse_args()

    print("=" * 67)
    print("   ClassBridge - Academic Neural Translation Fine-Tuner (EN↔VI)")
    print("=" * 67)

    pipeline = TranslationTrainerPipeline(model_name=args.model)
    pipeline.train_translation_lora(
        dataset_path=args.dataset,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
        lora_rank=args.lora_rank,
    )
