"""Merge a trained LoRA adapter and optionally export it for faster-whisper."""
# pyrefly: ignore-all-errors
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ── Auto-inject virtualenv ────────────────────────────────────────────────────
_VENV = Path(__file__).resolve().parent.parent / "backend" / "ai-service" / ".venv" / "Lib" / "site-packages"
if _VENV.exists() and str(_VENV) not in sys.path:
    sys.path.insert(0, str(_VENV))
# ─────────────────────────────────────────────────────────────────────────────


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-model", default="openai/whisper-base")
    parser.add_argument("--adapter", required=True)
    parser.add_argument("--merged-output", default="outputs/whisper-classbridge-base-merged")
    parser.add_argument("--ct2-output", default="")
    parser.add_argument("--quantization", default="int8")
    return parser.parse_args()


def main() -> None:
    from peft import PeftModel  # type: ignore[import]
    from transformers import WhisperForConditionalGeneration, WhisperProcessor  # type: ignore[import]

    args = parse_args()
    merged_output = Path(args.merged_output).resolve()
    base = WhisperForConditionalGeneration.from_pretrained(args.base_model)
    merged = PeftModel.from_pretrained(base, args.adapter).merge_and_unload()
    merged.save_pretrained(merged_output, safe_serialization=True)
    WhisperProcessor.from_pretrained(args.adapter).save_pretrained(merged_output)
    print(f"Merged Hugging Face model: {merged_output}")

    if args.ct2_output:
        ct2_output = Path(args.ct2_output).resolve()
        try:
            import ctranslate2  # type: ignore[import]
            from ctranslate2.converters import TransformersConverter

            class SafeTransformersConverter(TransformersConverter):
                def load_model(self, model_class, model_name_or_path, **kwargs):
                    if "dtype" in kwargs and kwargs["dtype"] is not None:
                        kwargs["torch_dtype"] = kwargs.pop("dtype")
                    return super().load_model(model_class, model_name_or_path, **kwargs)

            converter = SafeTransformersConverter(
                model_name_or_path=str(merged_output),
                copy_files=["preprocessor_config.json"],
            )
            converter.convert(
                output_dir=str(ct2_output),
                quantization=args.quantization,
                force=True,
            )
        except Exception:
            subprocess.run(
                [
                    "ct2-transformers-converter",
                    "--model", str(merged_output),
                    "--output_dir", str(ct2_output),
                    "--quantization", args.quantization,
                    "--copy_files", "tokenizer.json", "preprocessor_config.json",
                ],
                check=True,
            )
        print(f"faster-whisper model: {ct2_output}")


if __name__ == "__main__":
    main()
