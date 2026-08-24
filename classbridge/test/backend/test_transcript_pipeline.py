import sys
from pathlib import Path

# Add backend/ai-service to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend" / "ai-service"))

if sys.platform == "win32":
    reconfig_out = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfig_out):
        reconfig_out(encoding="utf-8")
    reconfig_err = getattr(sys.stderr, "reconfigure", None)
    if callable(reconfig_err):
        reconfig_err(encoding="utf-8")

from modules.correction_module import CorrectionModule
from modules.transcript_stabilizer import TranscriptStabilizer


def test_correction_module():
    print("[TEST CORRECTION] Chuẩn hóa và sửa lỗi âm gãy...")
    cm = CorrectionModule()

    # 1. Broken syllable
    broken = "tiế ng Việ t và ng oài"
    fixed = cm.clean(broken)
    print(f"  Broken: '{broken}' -> Fixed: '{fixed}'")
    assert "tiếng" in fixed and "Việt" in fixed and "ngoài" in fixed

    # 2. Repeated words
    rep = "Hello Hello everybody"
    fixed_rep = cm.clean(rep)
    print(f"  Rep: '{rep}' -> Fixed: '{fixed_rep}'")
    assert fixed_rep == "Hello everybody"

    print("  ✓ PASS Correction Module\n")


def test_stabilizer_progression():
    print("[TEST STABILIZER] Kiểm tra phân tách stable/unstable...")
    stab = TranscriptStabilizer(unstable_tail_words=1)

    # Chunk 1
    res1 = stab.process_partial("Hello")
    print(f"  Rev 1: stable='{res1.stable_text}', unstable='{res1.unstable_text}', full='{res1.full_text}'")
    assert res1.stable_text == "" and res1.unstable_text == "Hello" and res1.full_text == "Hello"

    # Chunk 2
    res2 = stab.process_partial("Hello everybody")
    print(f"  Rev 2: stable='{res2.stable_text}', unstable='{res2.unstable_text}', full='{res2.full_text}'")
    assert res2.stable_text == "Hello" and res2.unstable_text == "everybody" and res2.full_text == "Hello everybody"

    # Chunk 3 - Final
    res3 = stab.finalize("Hello everybody today.")
    print(f"  Final: stable='{res3.stable_text}', full='{res3.full_text}'")
    assert res3.is_final and res3.full_text == "Hello everybody today."

    print("  ✓ PASS Transcript Stabilizer\n")


if __name__ == "__main__":
    print("==========================================================================")
    print(" 🚀 RUNNING MODULAR PIPELINE TESTS")
    print("==========================================================================")
    test_correction_module()
    test_stabilizer_progression()
    print("==========================================================================")
    print(" 🏆 ALL MODULAR UNIT TESTS PASSED 100%")
    print("==========================================================================")
