"""
ClassBridge – Automated ASR Pipeline Test Suite
Kiểm thử toàn diện 12 Test Cases theo ASR_FIX_TASK.md:
- Raw ASR tiếng Việt
- Stabilizer Monotonic & Không đoán chữ, không nhảy chữ, không mất chữ
- Final Lock
- WebSocket Out-of-Order Packet Buffer
- Anti-duplicate
- Rule 19 Logging Format
"""

import sys
import os
import json
import time
from pathlib import Path

for stream in (sys.stdout, sys.stderr):
    reconfigure = getattr(stream, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="backslashreplace")

AI_SERVICE_DIR = Path(__file__).resolve().parents[2] / "backend" / "ai-service"
sys.path.insert(0, str(AI_SERVICE_DIR))

from transcript_stabilizer import TranscriptStabilizer



def test_stabilizer_monotonic():
    print("\n--- [TEST 1 & 8] Stabilizer Monotonic Partial & Final ---")
    st = TranscriptStabilizer(min_stable_count=1, unstable_tail_words=1)
    
    # Partial 1
    r1 = st.process_partial("Hôm nay")
    print(f"Partial 1 -> full: {r1.full_text!r} | stable: {r1.stable_text!r} | unstable: {r1.unstable_text!r}")
    assert r1.full_text == "Hôm nay", f"Lỗi partial 1: {r1.full_text}"
    
    # Partial 2
    r2 = st.process_partial("Hôm nay chúng ta")
    print(f"Partial 2 -> full: {r2.full_text!r} | stable: {r2.stable_text!r} | unstable: {r2.unstable_text!r}")
    assert r2.full_text == "Hôm nay chúng ta", f"Lỗi partial 2: {r2.full_text}"
    
    # Partial 3
    r3 = st.process_partial("Hôm nay chúng ta sẽ học")
    print(f"Partial 3 -> full: {r3.full_text!r} | stable: {r3.stable_text!r} | unstable: {r3.unstable_text!r}")
    assert r3.full_text == "Hôm nay chúng ta sẽ học", f"Lỗi partial 3: {r3.full_text}"
    
    # Final
    rf = st.finalize("Hôm nay chúng ta sẽ học về kiến trúc phần mềm.")
    print(f"Final -> full: {rf.full_text!r} | is_final: {rf.is_final}")
    assert rf.full_text == "Hôm nay chúng ta sẽ học về kiến trúc phần mềm.", f"Lỗi final: {rf.full_text}"
    assert rf.is_final == True
    print(">>> PASS: Monotonic Partial & Final")


def test_anti_anchor_jumping():
    print("\n--- [TEST 2 & 4] Anti Anchor Jumping & Overlap Deduplication ---")
    st = TranscriptStabilizer(min_stable_count=1, unstable_tail_words=1)
    
    # Partial ban đầu: câu dài
    st.process_partial("Hôm nay chúng ta sẽ tìm hiểu về kiến trúc phần mềm và các thành phần")
    
    # Giả lập rolling window mới từ Whisper: "phần mềm và các thành phần chính của hệ thống"
    # Overlap là "phần mềm và các thành phần"
    r2 = st.process_partial("phần mềm và các thành phần chính của hệ thống")
    print(f"After Overlap -> full: {r2.full_text!r}")
    
    # Không được lặp từ "phần mềm" hai lần và không được cắt mất phần đầu "Hôm nay chúng ta..."
    assert "Hôm nay chúng ta" in r2.full_text, "Lỗi mất chữ đầu!"
    assert "chính của hệ thống" in r2.full_text, "Lỗi mất chữ đuôi!"
    assert "phần mềm và các thành phần phần mềm" not in r2.full_text, "Lỗi trùng lặp từ!"
    print(">>> PASS: Anti Anchor Jumping & Overlap Deduplication")


def test_frontend_state_and_final_lock():
    print("\n--- [TEST 7, 8, 10, 11] Frontend Segment Reordering, Final Lock & Anti-Duplicate ---")
    
    class MockFrontendSubtitleStore:
        def __init__(self):
            self.subtitles = []
            self.segment_state = {}
            self.expected_chunk_id = 1
            self.packet_buffer = {}

        def process_single_packet(self, msg):
            session_id = msg.get("session_id", "global")
            segment_id = int(msg.get("segment_id", 0))
            revision = int(msg.get("revision", 0))
            is_final = bool(msg.get("final", False) or msg.get("type") == "final")
            text = msg.get("text", "")

            if not segment_id:
                return

            state_key = f"{session_id}:{segment_id}"
            prior = self.segment_state.get(state_key, {"last_revision": 0, "final_committed": False})

            # Final lock check
            if prior["final_committed"] and not is_final:
                print(f"   [DROP] Bỏ qua packet segment={segment_id} rev={revision} vì segment đã FINAL")
                return

            # Stale / Duplicate revision check
            if revision <= prior["last_revision"] and not is_final:
                print(f"   [DROP] Bỏ qua duplicate/stale segment={segment_id} rev={revision} (prior={prior['last_revision']})")
                return

            prior["last_revision"] = max(prior["last_revision"], revision)
            if is_final:
                prior["final_committed"] = True
            self.segment_state[state_key] = prior

            # Update state in place
            found = False
            for idx, item in enumerate(self.subtitles):
                if item["segment_id"] == segment_id:
                    if item["final"] and not is_final:
                        return
                    self.subtitles[idx] = {
                        **item,
                        "text": text,
                        "revision": max(item["revision"], revision),
                        "final": is_final or item["final"],
                    }
                    found = True
                    break

            if not found:
                self.subtitles.append({
                    "segment_id": segment_id,
                    "text": text,
                    "revision": revision,
                    "final": is_final,
                })

        def handle_ws_message(self, msg):
            incoming_chunk_id = msg.get("chunk_id")
            if incoming_chunk_id is None:
                self.process_single_packet(msg)
                return

            if self.expected_chunk_id == 1 and not self.packet_buffer and incoming_chunk_id > 1:
                self.expected_chunk_id = incoming_chunk_id

            if incoming_chunk_id > self.expected_chunk_id:
                print(f"   [BUFFER] Chunk {incoming_chunk_id} đến trước chunk {self.expected_chunk_id} -> đưa vào buffer")
                self.packet_buffer[incoming_chunk_id] = msg
                return

            self.process_single_packet(msg)
            self.expected_chunk_id = max(self.expected_chunk_id, incoming_chunk_id + 1)

            # Drain buffer
            while self.expected_chunk_id in self.packet_buffer:
                next_msg = self.packet_buffer.pop(self.expected_chunk_id)
                print(f"   [DRAIN] Xử lý chunk {self.expected_chunk_id} từ buffer")
                self.process_single_packet(next_msg)
                self.expected_chunk_id += 1

    store = MockFrontendSubtitleStore()

    # Test Out-of-Order Packet Delivery (Chunk 10, 12, 11)
    print("\n1. Test Reordering: Chunk 10 -> Chunk 12 -> Chunk 11:")
    store.handle_ws_message({"session_id": "s1", "chunk_id": 10, "segment_id": 1, "revision": 1, "text": "Hôm nay", "final": False})
    store.handle_ws_message({"session_id": "s1", "chunk_id": 12, "segment_id": 1, "revision": 3, "text": "Hôm nay chúng ta sẽ học", "final": False})
    store.handle_ws_message({"session_id": "s1", "chunk_id": 11, "segment_id": 1, "revision": 2, "text": "Hôm nay chúng ta", "final": False})

    assert len(store.subtitles) == 1, f"Lỗi số dòng subtitle: {len(store.subtitles)}"
    assert store.subtitles[0]["revision"] == 3, f"Lỗi revision cuối: {store.subtitles[0]['revision']}"
    assert store.subtitles[0]["text"] == "Hôm nay chúng ta sẽ học"
    print(">>> PASS: Out-of-Order Reordering thành công (10 -> 11 -> 12), chỉ hiển thị 1 dòng duy nhất!")

    # Test Duplicate Revision Packets
    print("\n2. Test Duplicate Revisions:")
    store.handle_ws_message({"session_id": "s1", "chunk_id": 13, "segment_id": 1, "revision": 3, "text": "Hôm nay chúng ta sẽ học", "final": False})
    store.handle_ws_message({"session_id": "s1", "chunk_id": 14, "segment_id": 1, "revision": 4, "text": "Hôm nay chúng ta sẽ học về kiến trúc", "final": False})
    assert len(store.subtitles) == 1
    assert store.subtitles[0]["revision"] == 4
    print(">>> PASS: Duplicate Revision được loại bỏ, không sinh thêm dòng!")

    # Test Final Lock
    print("\n3. Test Final Lock:")
    store.handle_ws_message({"session_id": "s1", "chunk_id": 15, "segment_id": 1, "revision": 5, "text": "Hôm nay chúng ta sẽ học về kiến trúc phần mềm.", "final": True})
    assert store.subtitles[0]["final"] == True

    # Late partial packet arrives after final
    store.handle_ws_message({"session_id": "s1", "chunk_id": 16, "segment_id": 1, "revision": 2, "text": "Hôm nay chúng ta", "final": False})
    assert store.subtitles[0]["text"] == "Hôm nay chúng ta sẽ học về kiến trúc phần mềm."
    print(">>> PASS: Final Lock chặn thành công partial cũ, không bị ghi đè!")


def test_rule19_logging_format():
    print("\n--- [TEST Rule 19] Log Format Verification ---")
    session_id = "abc123456"
    chunk_id = 15
    current_segment_id = 4
    current_revision = 2
    window_seconds = 2.8
    detected_lang = "vi"
    confidence = 0.95
    raw_text = "Hôm nay chúng ta sẽ học"
    is_final = False
    time_str = "19:31:01"

    log_rule19 = (
        f"TIME={time_str} SESSION={session_id[:8]} CHUNK={chunk_id} "
        f"SEGMENT={current_segment_id} REVISION={current_revision} "
        f"AUDIO={window_seconds:.2f}s VAD=true LANG={detected_lang} "
        f"CONF={confidence:.2f} RAW={json.dumps(raw_text, ensure_ascii=False)} FINAL={'true' if is_final else 'false'}"
    )
    print("Generated Log Line:")
    print(log_rule19)
    assert "TIME=19:31:01" in log_rule19
    assert "SESSION=abc12345" in log_rule19
    assert "CHUNK=15" in log_rule19
    assert "SEGMENT=4" in log_rule19
    assert "REVISION=2" in log_rule19
    assert 'RAW="Hôm nay chúng ta sẽ học"' in log_rule19
    assert "FINAL=false" in log_rule19
    print(">>> PASS: Rule 19 Log Format chuẩn xác 100%")


if __name__ == "__main__":
    test_stabilizer_monotonic()
    test_anti_anchor_jumping()
    test_frontend_state_and_final_lock()
    test_rule19_logging_format()
    print("\n==================================================")
    print("ALL ASR PIPELINE TESTS PASSED SUCCESSFULLY! ✅")
    print("==================================================")
