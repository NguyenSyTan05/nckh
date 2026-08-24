import asyncio
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np


CLASSBRIDGE_DIR = Path(__file__).resolve().parents[2]
SERVICE_DIR = CLASSBRIDGE_DIR / "backend" / "ai-service"
sys.path.insert(0, str(SERVICE_DIR))
SPEC = importlib.util.spec_from_file_location("classbridge_ai", SERVICE_DIR / "main.py")
assert SPEC and SPEC.loader
ai = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ai)

TRAINER_SPEC = importlib.util.spec_from_file_location(
    "correction_trainer",
    CLASSBRIDGE_DIR / "training" / "train_correction_memory.py",
)
assert TRAINER_SPEC and TRAINER_SPEC.loader
correction_trainer = importlib.util.module_from_spec(TRAINER_SPEC)
TRAINER_SPEC.loader.exec_module(correction_trainer)


class TextAndLanguageTests(unittest.TestCase):
    def test_rejects_uncertain_short_guesses(self):
        self.assertTrue(ai.is_low_confidence_fragment("Bồ Thai Ba Bồ", 0.20))
        self.assertTrue(ai.is_low_confidence_fragment("Tinh chí xiao", 0.12))
        self.assertFalse(ai.is_low_confidence_fragment("Hello", 0.72))

    def test_keeps_meaningful_single_syllable_words(self):
        for word in ("ừ", "à", "ạ", "I", "a"):
            with self.subTest(word=word):
                self.assertEqual(ai.clean_recognized_text(word), word)
        self.assertEqual(ai.clean_recognized_text("1 **T"), "")

    def test_vietnamese_text_normalization(self):
        self.assertEqual(
            ai.normalize_vietnamese_text("nhận dạng giọng nói , phần mềm . ."),
            "nhận dạng giọng nói, phần mềm.",
        )

    def test_auto_language_is_restricted_to_english_and_vietnamese(self):
        probabilities = [("ja", 0.72), ("vi", 0.16), ("en", 0.08)]
        language, confidence = ai.choose_supported_language(probabilities)
        self.assertEqual(language, "vi")
        self.assertAlmostEqual(confidence, 2 / 3)

    def test_context_breaks_only_a_close_language_tie(self):
        probabilities = [("en", 0.24), ("vi", 0.22), ("zh", 0.40)]
        language, _ = ai.choose_supported_language(
            probabilities,
            "Hôm nay chúng ta học nhận dạng giọng nói.",
        )
        self.assertEqual(language, "vi")

    def test_rejects_scripts_outside_english_and_vietnamese(self):
        self.assertTrue(ai.contains_unsupported_script("目前到底 ピザ"))
        self.assertTrue(ai.contains_unsupported_script("กรสดงงดวยเมงดหลายเท่า"))
        self.assertEqual(ai.clean_recognized_text("กรสดงงดวยเมงดหลายเท่า"), "")
        self.assertFalse(ai.contains_unsupported_script("Hôm nay we learn AI"))

    def test_final_pass_keeps_the_trained_recognizer(self):
        self.assertEqual(ai.WHISPER_ACCURATE_MODEL, ai.WHISPER_MODEL)

    def test_review_gate_only_uses_llm_for_hard_cases(self):
        easy_source = "Today we study software testing"
        easy_translation = "Hôm nay chúng ta học kiểm thử phần mềm"
        self.assertFalse(
            ai.needs_llm_review(easy_source, easy_translation, 0.84)
        )

    def test_mixed_vietnamese_translation_preserves_technical_term(self):
        repaired = ai.apply_translation_glossary(
            "Em chưa hiểu boundary value analysis.",
            "I don't understand Parundary value analysis.",
            "vi",
        )
        self.assertEqual(
            repaired,
            "I don't understand boundary value analysis.",
        )
        self.assertTrue(
            ai.needs_llm_review(
                "Today we study API and SQL with ClassBridge",
                "Hôm nay chúng ta học API và SQL với ClassBridge",
                0.84,
            )
        )


class CorrectionMemoryTests(unittest.TestCase):
    def test_trainer_learns_only_repeated_verified_substitutions(self):
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "pairs.jsonl"
            input_path.write_text(
                "\n".join(
                    [
                        '{"raw":"nhận dạng dọng nói","corrected":"nhận dạng giọng nói","language":"vi"}',
                        '{"raw":"mô hình dọng nói","corrected":"mô hình giọng nói","language":"vi"}',
                        '{"raw":"lỗi một lần","corrected":"lỗi khác","language":"vi"}',
                    ]
                ),
                encoding="utf-8",
            )
            rules = correction_trainer.train(input_path, 2, 0.8, 5)
        self.assertEqual(len(rules), 1)
        self.assertEqual(rules[0]["source"], "dọng")
        self.assertEqual(rules[0]["target"], "giọng")

    def test_runtime_applies_only_matching_language_rules(self):
        with tempfile.TemporaryDirectory() as directory:
            memory_path = Path(directory) / "memory.json"
            memory_path.write_text(
                '{"version":1,"rules":['
                '{"source":"dọng nói","target":"giọng nói",'
                '"language":"vi","support":3,"confidence":1.0}]}'
                ,
                encoding="utf-8",
            )
            self.assertEqual(
                ai.apply_correction_memory(
                    "Nhận dạng dọng nói", "vi", str(memory_path)
                ),
                "Nhận dạng giọng nói",
            )
            self.assertEqual(
                ai.apply_correction_memory(
                    "Nhận dạng dọng nói", "en", str(memory_path)
                ),
                "Nhận dạng dọng nói",
            )


if __name__ == "__main__":
    unittest.main()
