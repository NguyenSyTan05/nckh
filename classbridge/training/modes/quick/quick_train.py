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
PIPELINE = TRAINING_ROOT / "train_ai_pipeline.py"
VENV_PYTHON = PROJECT_ROOT / "backend" / "ai-service" / ".venv" / "Scripts" / "python.exe"


def resolve_python() -> str:
    return str(VENV_PYTHON) if VENV_PYTHON.exists() else sys.executable


def run_pipeline(mode: str, manifest: str) -> None:
    cmd = [
        resolve_python(),
        str(PIPELINE),
        "--mode",
        mode,
        "--manifest",
        manifest,
    ]
    print(f"\n[Quick Mode] Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def main() -> None:
    parser = argparse.ArgumentParser(description="Quick training mode for fast validation and baseline checks.")
    parser.add_argument("--mode", choices=["nmt", "all", "eval"], default="nmt", help="Quick mode selected for validation/training")
    parser.add_argument(
        "--manifest",
        default=str(PROJECT_ROOT / "backend" / "data" / "bilingual_sample_manifest.jsonl"),
        help="Manifest used by the quick pipeline",
    )
    args = parser.parse_args()

    print("=" * 72)
    print("  QUICK TRAIN MODE (baseline / check pipeline)")
    print("=" * 72)
    print("  Purpose: fast validation, sample training, quick NMT test")
    print("  Folder : classbridge/training/modes/quick")
    print("=" * 72)
    run_pipeline(args.mode, args.manifest)


if __name__ == "__main__":
    main()
