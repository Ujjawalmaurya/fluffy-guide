"""
demo/router.py — Pre-seeded demo login personas for hackathon judging.
POST /api/demo/login  — Returns a JWT for a demo persona without OTP.
"""
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from supabase import create_client

router = APIRouter(prefix="/api/demo", tags=["Demo"])

PERSONAS = {
    "ramesh": {
        "email": "demo.ramesh@sankalp.ai",
        "password": os.getenv("DEMO_PASSWORD", "DemoSankalp2025!"),
        "label": "Ramesh - Rural Tech Aspirant",
    },
    "priya": {
        "email": "demo.priya@sankalp.ai",
        "password": os.getenv("DEMO_PASSWORD", "DemoSankalp2025!"),
        "label": "Priya - Healthcare Professional",
    },
    "officer": {
        "email": "demo.officer@sankalp.ai",
        "password": os.getenv("DEMO_PASSWORD", "DemoSankalp2025!"),
        "label": "Officer - Government Evaluator",
    },
}


class DemoLoginRequest(BaseModel):
    persona: str  # 'ramesh' | 'priya' | 'officer'


@router.post("/login")
async def demo_login(req: DemoLoginRequest):
    persona = PERSONAS.get(req.persona.lower())
    if not persona:
        raise HTTPException(status_code=400, detail=f"Unknown persona. Choose from: {list(PERSONAS.keys())}")
    
    supabase_url = os.getenv("SUPABASE_URL", "")
    supabase_key = os.getenv("SUPABASE_ANON_KEY", "")
    
    if not supabase_url or not supabase_key:
        raise HTTPException(status_code=503, detail="Supabase not configured")
    
    client = create_client(supabase_url, supabase_key)
    
    try:
        session = client.auth.sign_in_with_password({
            "email": persona["email"],
            "password": persona["password"],
        })
        return {
            "success": True,
            "data": {
                "persona": req.persona,
                "label": persona["label"],
                "access_token": session.session.access_token,
                "refresh_token": session.session.refresh_token,
                "token_type": "bearer",
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Demo login failed. Ensure demo users exist in Supabase. Error: {str(e)}"
        )


@router.get("/personas")
async def list_personas():
    return {
        "success": True,
        "data": [
            {"id": k, "label": v["label"]}
            for k, v in PERSONAS.items()
        ]
    }
