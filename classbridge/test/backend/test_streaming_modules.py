import os
import sys
import unittest
from pathlib import Path

# Force UTF-8 output on Windows console
os.environ["PYTHONIOENCODING"] = "utf-8"
for stream in (sys.stdout, sys.stderr):
    reconfigure = getattr(stream, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="replace")

# Add ai-service directory to sys.path
ai_service_dir = Path(__file__).resolve().parents[2] / "backend" / "ai-service"
if str(ai_service_dir) not in sys.path:
    sys.path.insert(0, str(ai_service_dir))

from transcript_stabilizer import TranscriptStabilizer
from auto_punctuation import format_auto_punctuation, preserve_code_switching, remove_repetitions


class TestTranscriptStabilizer(unittest.TestCase):
    def test_stabilizer_partial_flow(self):
        stabilizer = TranscriptStabilizer(min_stable_count=1)
        
        # Step 1: "Software testing"
        res1 = stabilizer.process_partial("Software testing")
        self.assertEqual(res1.full_text, "Software testing")
        
        # Step 2: "Software testing helps"
        res2 = stabilizer.process_partial("Software testing helps")
        self.assertTrue("Software" in res2.stable_text)
        self.assertTrue("testing" in res2.stable_text)
        
        # Step 3: Finalize
        res3 = stabilizer.finalize("Software testing helps software quality.")
        self.assertTrue(res3.is_final)
        self.assertEqual(res3.stable_text, "Software testing helps software quality.")
        self.assertEqual(res3.unstable_text, "")

    def test_stabilizer_divergent_flow(self):
        stabilizer = TranscriptStabilizer(min_stable_count=1, unstable_tail_words=2)
        stabilizer.process_partial("Software testing")
        stabilizer.process_partial("Software testing helps")
        
        # Divergence: Whisper changes first word
        res = stabilizer.process_partial("Hardware testing helps quality")
        # Confirmed words must not jump when a rolling-window hypothesis
        # briefly revises the beginning of the sentence.
        self.assertEqual(res.stable_text, "Software testing")
        self.assertEqual(res.unstable_text, "helps quality")

    def test_stabilizer_keeps_prefix_when_rolling_window_moves(self):
        stabilizer = TranscriptStabilizer(min_stable_count=1)
        stabilizer.process_partial("one two three four")
        stabilizer.process_partial("one two three four five")

        # The recognizer's short window has dropped "one two". The confirmed
        # document prefix must stay in place and only the new suffix is added.
        res = stabilizer.process_partial("three four five six")
        self.assertEqual(res.full_text, "one two three four five six")

    def test_code_switching_and_punctuation(self):
        text = "thầy cho em hỏi cái boundary value này chạy như thế nào"
        formatted = format_auto_punctuation(text, "vi")
        self.assertTrue("boundary value" in formatted)
        self.assertTrue(formatted.startswith("Thầy"))
        self.assertTrue(formatted.endswith("?"))

    def test_remove_repetitions(self):
        t1 = "Giáo trình công nghệ, phần mềm, phần mềm."
        self.assertEqual(remove_repetitions(t1), "Giáo trình công nghệ, phần mềm.")

        t2 = "Technology, software, software."
        self.assertEqual(remove_repetitions(t2), "Technology, software.")

        t3 = "Tôi tôi muốn học môn này."
        self.assertEqual(remove_repetitions(t3), "Tôi muốn học môn này.")

        t4 = "Giáo trình công nghệ, phần mềm, phần mềm, phần mềm!"
        self.assertEqual(remove_repetitions(t4), "Giáo trình công nghệ, phần mềm!")


if __name__ == "__main__":
    unittest.main()
