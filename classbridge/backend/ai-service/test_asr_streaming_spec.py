"""
Test suite redirect — Main test suite has moved to classbridge/test/backend/test_asr_streaming_spec.py
"""

import sys
from pathlib import Path

TEST_SUITE_PATH = Path(__file__).resolve().parents[1] / "test" / "backend" / "test_asr_streaming_spec.py"
sys.path.insert(0, str(TEST_SUITE_PATH.parent))

if __name__ == "__main__":
    import test_asr_streaming_spec
    test_asr_streaming_spec.test_1_vietnamese()
    test_asr_streaming_spec.test_2_long_continuous_speech()
    test_asr_streaming_spec.test_3_overlap_merge()
    test_asr_streaming_spec.test_4_out_of_order_packets()
    test_asr_streaming_spec.test_5_duplicate_revision_drop()
    test_asr_streaming_spec.test_6_final_lock()
    test_asr_streaming_spec.test_7_language_vi()
    test_asr_streaming_spec.test_8_language_en()
    test_asr_streaming_spec.test_9_mixed_language()
    test_asr_streaming_spec.test_10_silence_and_no_hallucination()
    test_asr_streaming_spec.test_11_rapid_speech()
    test_asr_streaming_spec.test_12_continuous_stream_60s()
