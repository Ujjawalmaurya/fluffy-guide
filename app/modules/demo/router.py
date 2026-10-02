"""
router.py — Pre-seeded demo login personas for hackathon judging.
POST /api/v1/demo/login — Returns a JWT for a demo persona without OTP.
"""
from fastapi import APIRouter, HTTPException
from app.modules.demo.personas import PERSONA_MAP
from app.modules.demo.schemas import DemoLoginRequest
from app.modules.demo.service import demo_service

router = APIRouter(prefix="/demo", tags=["Demo"])


@router.post("/login")
async def demo_login(request: DemoLoginRequest):
    data = demo_service.login_persona(request.persona)
    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"Persona not found. Choose from: {list(PERSONA_MAP.keys())}",
        )

    return {
        "success": True,
        "data": data,
    }
