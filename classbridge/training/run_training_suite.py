from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent


def run(cmd: list[str]) -> None:
    print(f"\n>> {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(PROJECT_DIR), text=True)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def main() -> None:
    run([sys.executable, str(BASE_DIR / "prepare_balanced_multilingual_manifest.py")])
    run([
        sys.executable,
        str(BASE_DIR / "train_balanced_translation.py"),
        "--dataset",
        str(PROJECT_DIR / "data" / "manifests" / "translation_balanced.jsonl"),
        "--epochs",
        "2",
        "--batch-size",
        "2",
        "--lr",
        "5e-5",
        "--lora-rank",
        "16",
    ])

    print("\nTraining suite complete.")


if __name__ == "__main__":
    main()
