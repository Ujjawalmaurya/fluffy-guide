
from fastapi import APIRouter, Depends, HTTPException
from app.shared.dependencies import get_officer_user
from app.core.database import get_supabase
from app.core.logger import get_logger

router = APIRouter(prefix="/government", tags=["Government"])
log = get_logger("GOVERNMENT")

@router.get("/stats")
async def get_global_stats(current_user: dict = Depends(get_officer_user)):
    """
    Returns global workforce statistics for government officers.
    """
    db = get_supabase()
    try:
        # Get total users
        users_count = db.table("users").select("id", count="exact").execute()
        
        # Get jobs count
        jobs_count = db.table("jobs").select("id", count="exact").execute()
        
        # Get assessments count
        assessments_count = db.table("assessments").select("id", count="exact").execute()
        
        return {
            "success": True,
            "data": {
                "total_youth_registered": users_count.count or 0,
                "total_jobs_available": jobs_count.count or 0,
                "total_assessments_completed": assessments_count.count or 0,
                "active_programs": 12,  # Mocked for now
                "placement_rate": "68%"  # Mocked for now
            }
        }
    except Exception as e:
        log.error(f"Error fetching government stats: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/youth-list")
async def get_youth_list(current_user: dict = Depends(get_officer_user)):
    """
    Returns a list of youth profiles for monitoring.
    """
    db = get_supabase()
    try:
        res = db.table("users").select("id, email, user_type, created_at").limit(50).execute()
        return {
            "success": True,
            "data": res.data
        }
    except Exception as e:
        log.error(f"Error fetching youth list: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
