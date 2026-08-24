from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from datasets import Dataset
from peft import LoraConfig, TaskType, get_peft_model
from transformers import (
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    DataCollatorForSeq2Seq,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
)


BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
AI_SERVICE_DIR = PROJECT_DIR / "backend" / "ai-service"
DEFAULT_MODEL = "VietAI/envit5-translation"
OUTPUT_DIR = AI_SERVICE_DIR / "nmt-academic-lora-balanced"


def load_rows(path: Path) -> list[dict]:
    rows: list[dict] = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            source = str(row.get("source") or "").strip()
            target = str(row.get("target") or "").strip()
            if not source or not target:
                continue
            rows.append({
                "source": source,
                "target": target,
                "direction": str(row.get("direction") or "en2vi"),
                "language": str(row.get("language") or ("en" if source.lower().startswith("en:") else "vi")),
                "region": str(row.get("region") or "mixed"),
                "accent": str(row.get("accent") or "mixed"),
            })
    return rows


def make_dataset(rows: list[dict]) -> Dataset:
    return Dataset.from_list(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Train a balanced EN↔VI translation model with region/accent metadata.")
    parser.add_argument("--dataset", type=Path, default=Path("data/manifests/translation_balanced.jsonl"), help="Balanced JSONL dataset")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Base HuggingFace translation model")
    parser.add_argument("--epochs", type=int, default=3, help="Training epochs")
    parser.add_argument("--batch-size", type=int, default=2, help="Batch size")
    parser.add_argument("--lr", type=float, default=5e-5, help="Learning rate")
    parser.add_argument("--lora-rank", type=int, default=16, help="LoRA rank")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR, help="Where to save model")
    args = parser.parse_args()

    rows = load_rows(args.dataset)
    if not rows:
        raise SystemExit(f"No rows found in {args.dataset}. Run prepare_balanced_multilingual_manifest.py first.")

    dataset = make_dataset(rows)

    def preprocess(examples):
        source_texts = examples["source"]
        target_texts = examples["target"]
        source_inputs = tokenizer(source_texts, max_length=256, truncation=True, padding="max_length")
        target_inputs = tokenizer(target_texts, max_length=256, truncation=True, padding="max_length")
        pad_id = tokenizer.pad_token_id
        labels = []
        for ids in target_inputs["input_ids"]:
            labels.append([t if t != pad_id else -100 for t in ids])
        source_inputs["labels"] = labels
        return source_inputs

    tokenizer = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForSeq2SeqLM.from_pretrained(args.model)
    lora_config = LoraConfig(
        task_type=TaskType.SEQ_2_SEQ_LM,
        r=args.lora_rank,
        lora_alpha=args.lora_rank * 2,
        target_modules=["q", "v"],
        lora_dropout=0.05,
        bias="none",
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    tokenized = dataset.map(preprocess, batched=True, remove_columns=dataset.column_names)
    split = tokenized.train_test_split(test_size=0.15, seed=42)
    train_ds = split["train"]
    eval_ds = split["test"]

    collator = DataCollatorForSeq2Seq(tokenizer, model=model, padding=True, label_pad_token_id=-100)
    training_args = Seq2SeqTrainingArguments(
        output_dir=str(args.output_dir),
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        gradient_accumulation_steps=2,
        learning_rate=args.lr,
        warmup_ratio=0.1,
        num_train_epochs=args.epochs,
        eval_strategy="epoch",
        save_strategy="epoch",
        save_total_limit=2,
        predict_with_generate=True,
        generation_max_length=256,
        logging_steps=10,
        report_to="none",
        remove_unused_columns=False,
    )

    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=eval_ds,
        data_collator=collator,
        processing_class=tokenizer,
    )

    print(f"\n[Balanced NMT] Starting training with {len(train_ds)} train rows and {len(eval_ds)} eval rows")
    start = time.time()
    trainer.train()
    elapsed = time.time() - start

    args.output_dir.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(str(args.output_dir))
    tokenizer.save_pretrained(str(args.output_dir))

    meta = {
        "base_model": args.model,
        "dataset": str(args.dataset),
        "epochs": args.epochs,
        "batch_size": args.batch_size,
        "learning_rate": args.lr,
        "lora_rank": args.lora_rank,
        "train_rows": len(train_ds),
        "eval_rows": len(eval_ds),
        "duration_seconds": round(elapsed, 2),
    }
    (args.output_dir / "classbridge_balanced_nmt_config.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[Balanced NMT] Training complete in {elapsed:.1f}s")
    print(f"[Balanced NMT] Model saved to {args.output_dir}")


if __name__ == "__main__":
    main()
