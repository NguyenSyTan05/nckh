import unittest
import asyncio
import sys
from pathlib import Path

ai_service_dir = Path(__file__).resolve().parents[2] / "backend" / "ai-service"
if str(ai_service_dir) not in sys.path:
    sys.path.insert(0, str(ai_service_dir))

from session_manager import session_manager, generate_join_code


class TestSessionManager(unittest.TestCase):
    def test_join_code_format(self):
        code = generate_join_code()
        self.assertTrue(code.startswith("DTU-"))
        self.assertEqual(len(code), 7)

    def test_session_lifecycle(self):
        async def _run():
            session = await session_manager.create_session("test_sess_001", "auto")
            self.assertEqual(session.session_id, "test_sess_001")
            self.assertTrue(session.join_code.startswith("DTU-"))

            by_code = await session_manager.get_by_code(session.join_code)
            self.assertIsNotNone(by_code)
            self.assertEqual(by_code.session_id, "test_sess_001")

            active = await session_manager.list_active_sessions()
            self.assertGreaterEqual(len(active), 1)

            await session_manager.remove_session("test_sess_001")
            removed = await session_manager.get_by_code(session.join_code)
            self.assertIsNone(removed)

        asyncio.run(_run())


if __name__ == "__main__":
    unittest.main()
