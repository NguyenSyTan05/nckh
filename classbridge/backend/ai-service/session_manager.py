"""
ClassBridge – Classroom Session & Multi-Client Broadcast Manager
"""

from __future__ import annotations

import asyncio
import random
import string
import time
from typing import Dict, List, Set, Any
from fastapi import WebSocket


def generate_join_code() -> str:
    """Tạo mã lớp học ngắn gọn dễ nhớ 6 ký tự, ví dụ: DTU-882."""
    digits = "".join(random.choices(string.digits, k=3))
    return f"DTU-{digits}"


class ClassroomSession:
    def __init__(self, session_id: str, join_code: str, language: str = "auto"):
        self.session_id = session_id
        self.join_code = join_code
        self.language = language
        self.created_at = time.time()
        self.teacher_ws: WebSocket | None = None
        self.student_sockets: Set[WebSocket] = set()
        self.subtitles_history: List[dict] = []
        self.context = ""

    async def broadcast(self, message: dict):
        """Gửi message tới tất cả các sinh viên đang kết nối vào lớp học."""
        disconnected = set()
        for ws in list(self.student_sockets):
            try:
                await ws.send_json(message)
            except Exception:
                disconnected.add(ws)

        for ws in disconnected:
            self.student_sockets.discard(ws)

    async def close_students(self) -> None:
        """Close all read-only viewers when the teacher stream ends."""
        sockets = list(self.student_sockets)
        self.student_sockets.clear()
        for ws in sockets:
            try:
                await ws.close(code=1000, reason="Phiên học đã kết thúc.")
            except Exception:
                pass


class SessionManager:
    def __init__(self):
        self._sessions_by_id: Dict[str, ClassroomSession] = {}
        self._sessions_by_code: Dict[str, ClassroomSession] = {}
        self._lock = asyncio.Lock()

    async def create_session(self, session_id: str = "", language: str = "auto") -> ClassroomSession:
        async with self._lock:
            sid = session_id.strip() or f"session_{int(time.time())}"
            join_code = generate_join_code()
            while join_code in self._sessions_by_code:
                join_code = generate_join_code()

            session = ClassroomSession(sid, join_code, language)
            self._sessions_by_id[sid] = session
            self._sessions_by_code[join_code] = session
            return session

    async def get_by_id(self, session_id: str) -> ClassroomSession | None:
        async with self._lock:
            return self._sessions_by_id.get(session_id)

    async def get_by_code(self, join_code: str) -> ClassroomSession | None:
        async with self._lock:
            return self._sessions_by_code.get(join_code.upper().strip())

    async def remove_session(self, session_id: str):
        session = None
        async with self._lock:
            session = self._sessions_by_id.pop(session_id, None)
            if session:
                self._sessions_by_code.pop(session.join_code, None)
        if session:
            await session.close_students()

    async def list_active_sessions(self) -> List[dict]:
        async with self._lock:
            return [
                {
                    "session_id": s.session_id,
                    "join_code": s.join_code,
                    "student_count": len(s.student_sockets),
                    "created_at": s.created_at,
                    "subtitles_count": len(s.subtitles_history),
                }
                for s in self._sessions_by_id.values()
            ]


# Singleton global session manager
session_manager = SessionManager()
