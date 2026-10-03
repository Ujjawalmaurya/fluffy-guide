"""
session_store.py — Thread-safe in-memory store for active mock interview sessions.
"""
from typing import Dict, Any, Optional

_sessions: Dict[str, Dict[str, Any]] = {}


class InterviewSessionStore:
    @staticmethod
    def get_session(session_id: str) -> Optional[Dict[str, Any]]:
        return _sessions.get(session_id)

    @staticmethod
    def save_session(session_id: str, data: Dict[str, Any]):
        _sessions[session_id] = data

    @staticmethod
    def delete_session(session_id: str):
        _sessions.pop(session_id, None)


session_store = InterviewSessionStore()
