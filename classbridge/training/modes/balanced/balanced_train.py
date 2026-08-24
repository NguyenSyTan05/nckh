from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parents[3]
TRAINING_ROOT = PROJECT_ROOT / "training"
PREPARE = TRAINING_ROOT / "prepare_balanced_multilingual_manifest.py"
TRAIN = TRAINING_ROOT / "train_balanced_translation.py"
VENV_PYTHON = PROJECT_ROOT / "backend" / "ai-service" / ".venv" / "Scripts" / "python.exe"


def resolve_python() -> str:
    return str(VENV_PYTHON) if VENV_PYTHON.exists() else sys.executable


def run_step(cmd: list[str]) -> None:
    print(f"\n[Balanced Mode] Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def main() -> None:
    parser = argparse.ArgumentParser(description="Balanced production mode for region-aware EN↔VI training.")
    parser.add_argument("--input", type=Path, default=PROJECT_ROOT / "data" / "manifests" / "translation_pairs_fixed.jsonl", help="Input translation pairs")
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "data" / "manifests" / "translation_balanced.jsonl", help="Output balanced manifest")
    parser.add_argument("--epochs", type=int, default=2, help="Epochs for balanced training")
    parser.add_argument("--batch-size", type=int, default=2, help="Batch size")
    parser.add_argument("--lr", type=float, default=5e-5, help="Learning rate")
    parser.add_argument("--lora-rank", type=int, default=16, help="LoRA rank")
    args = parser.parse_args()

    print("=" * 72)
    print("  BALANCED TRAIN MODE (production / region-aware)")
    print("=" * 72)
    print("  Purpose: balanced EN/VI data across regions and accents")
    print("  Folder : classbridge/training/modes/balanced")
    print("=" * 72)

    prepare_cmd = [
        resolve_python(),
        str(PREPARE),
        "--input",
        str(args.input),
        "--output",
        str(args.output),
    ]
    run_step(prepare_cmd)

    train_cmd = [
        resolve_python(),
        str(TRAIN),
        "--dataset",
        str(args.output),
        "--epochs",
        str(args.epochs),
        "--batch-size",
        str(args.batch_size),
        "--lr",
        str(args.lr),
        "--lora-rank",
        str(args.lora_rank),
    ]
    run_step(train_cmd)


if __name__ == "__main__":
    main()
