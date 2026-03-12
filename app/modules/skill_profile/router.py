from fastapi import APIRouter, Depends
from loguru import logger
from supabase import Client

from app.shared.dependencies import get_current_user, get_db
from app.modules.skill_profile.repository import SkillProfileRepository
from app.modules.skill_profile.service import SkillProfileService

router = APIRouter(prefix="/skills", tags=["Skill Profile"])

def get_skill_profile_service(db: Client = Depends(get_db)) -> SkillProfileService:
    repo = SkillProfileRepository(db)
    return SkillProfileService(repo)

@router.get("/me", response_model=dict)
async def get_my_profile(
    user: dict = Depends(get_current_user),
    service: SkillProfileService = Depends(get_skill_profile_service)
):
    user_id = user["id"]
    profile = service.get_profile(user_id)
    
    logger.info(f"[SKILL_PROFILE] [INFO] Profile fetched for user={user_id}")
    
    return {
        "success": True,
        "data": profile.model_dump()
    }

@router.get("/me/summary", response_model=dict)
async def get_my_summary(
    user: dict = Depends(get_current_user),
    service: SkillProfileService = Depends(get_skill_profile_service)
):
    user_id = user["id"]
    summary = service.get_summary(user_id)
    
    return {
        "success": True,
        "data": summary.model_dump()
    }
