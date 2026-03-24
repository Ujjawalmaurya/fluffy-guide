"""
demo/router.py — Pre-seeded demo login personas for hackathon judging.
POST /api/v1/demo/login  — Returns a JWT for a demo persona without OTP.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.security import create_access_token, create_refresh_token

router = APIRouter(prefix="/demo", tags=["Demo"])

# Unified Persona Configuration
PERSONA_MAP = {
    "ravi": {
        "id": "daa14278-f26b-4404-95cc-5eb169925fed",
        "email": "ravi@demo.sankalp.gov.in",
        "name": "Ravi Kumar",
        "type": "rural_tech"
    },
    "meera": {
        "id": "cea951a5-b448-4dc4-8c37-b83d1d5b689b",
        "email": "meera@demo.sankalp.gov.in",
        "name": "Meera Devi",
        "type": "shg_leader"
    },
    "arjun": {
        "id": "52001edf-a140-4d78-9e33-4705ffeed9e8",
        "email": "arjun@demo.sankalp.gov.in",
        "name": "Arjun Subramanian",
        "type": "msme_owner"
    },
    "admin": {
        "id": "63112fdf-b251-5e89-1e44-5816ffeea1b9",
        "email": "admin@sankalp.gov.in",
        "name": "System Admin",
        "type": "admin"
    }
}

class DemoLoginRequest(BaseModel):
    persona: str  # 'ravi' | 'meera' | 'arjun' | 'admin'

@router.post("/login")
async def demo_login(request: DemoLoginRequest):
    p_key = request.persona.lower()
    if p_key not in PERSONA_MAP:
        raise HTTPException(
            status_code=404, 
            detail=f"Persona not found. Choose from: {list(PERSONA_MAP.keys())}"
        )
        
    user_info = PERSONA_MAP[p_key]
    
    # Generate tokens using backend secret
    # Using 'sub' as the UUID for consistency with Supabase Auth
    access_token = create_access_token(user_id=user_info["id"], data={"persona": p_key})
    refresh_token = create_refresh_token(user_id=user_info["id"])
    
    return {
        "success": True,
        "data": {
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
                "full_name": user_info["name"]
            }
        }
    }
