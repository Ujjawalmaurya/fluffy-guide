from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any
from app.shared.dependencies import get_current_user
from app.services.job_recommendation_service import JobRecommendationService
from app.services.career_identity_service import CareerIdentityService
from app.core.logger import get_logger

router = APIRouter(
    prefix="/api/v1/recommendations",
    tags=["recommendations"]
)

log = get_logger("RECOMMENDATIONS_ROUTER")

@router.get("/jobs")
async def get_job_recommendations(
    current_user: Dict[str, Any] = Depends(get_current_user),
    limit: int = Query(5, ge=1, le=20),
    threshold: float = Query(0.5, ge=0.0, le=1.0)
):
    """
    Get personalized job recommendations for the current user.
    Uses AI-generated career identity and vector similarity.
    """
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(status_code=401, detail="User not authenticated")
        
    log.info(f"Fetching recommendations for user {user_id}")
    
    try:
        recommendations = await JobRecommendationService.get_recommendations(
            user_id=user_id,
            limit=limit,
            match_threshold=threshold
        )
        return {"recommendations": recommendations}
    except Exception as e:
        log.error(f"Failed to get recommendations for {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while fetching recommendations")

@router.post("/identity/refresh")
async def refresh_career_identity(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Force a re-generation of the user's career identity persona and embedding.
    Useful when the user updates their profile or preferences significantly.
    """
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(status_code=401, detail="User not authenticated")
        
    log.info(f"Refreshing career identity for user {user_id}")
    
    try:
        service = CareerIdentityService()
        await service.generate_and_store_identity(user_id)
        return {"status": "success", "message": "Career identity refreshed successfully"}
    except Exception as e:
        log.error(f"Identity refresh failed for {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to refresh career identity")

@router.get("/identity")
async def get_career_identity(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Fetches the current user's AI-generated career persona.
    """
    from app.core.database import get_supabase
    user_id = current_user.get("id")
    
    supabase = get_supabase()
    res = supabase.table("user_profiles").select("career_identity").eq("user_id", user_id).single().execute()
    
    if not res.data:
        return {"identity": None}
        
    return {"identity": res.data.get("career_identity")}
