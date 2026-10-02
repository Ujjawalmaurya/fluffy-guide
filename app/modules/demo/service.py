"""
service.py — Demo login token generator and persona manager.
"""
from typing import Optional, Dict, Any
from app.core.security import create_access_token, create_refresh_token
from app.modules.demo.personas import PERSONA_MAP


class DemoService:
    @staticmethod
    def get_persona(persona_key: str) -> Optional[Dict[str, Any]]:
        return PERSONA_MAP.get(persona_key.lower())

    @staticmethod
    def login_persona(persona_key: str) -> Optional[Dict[str, Any]]:
        user_info = DemoService.get_persona(persona_key)
        if not user_info:
            return None

        p_key = persona_key.lower()
        access_token = create_access_token(user_id=user_info["id"], data={"persona": p_key})
        refresh_token = create_refresh_token(user_id=user_info["id"])

        return {
            "persona": p_key,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user_info["id"],
                "email": user_info["email"],
                "user_type": user_info["type"],
                "preferred_lang": "en",
                "onboarding_done": True,
                "full_name": user_info["name"],
            },
        }


demo_service = DemoService()
