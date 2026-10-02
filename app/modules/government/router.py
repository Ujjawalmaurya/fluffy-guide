"""
router.py — Government officer portal endpoints.
Prefix: /government (mounted under /api/v1 in main.py)
"""
from fastapi import APIRouter, Depends, HTTPException
from app.shared.dependencies import get_officer_user, get_db
from app.core.logger import get_logger
from app.modules.government.repository import GovernmentRepository
from app.modules.government.service import GovernmentService

router = APIRouter(prefix="/government", tags=["Government"])
log = get_logger("GOVERNMENT")


@router.get("/stats")
async def get_global_stats(
    current_user: dict = Depends(get_officer_user),
    db=Depends(get_db),
):
    """Returns global workforce statistics for government officers."""
    try:
        repo = GovernmentRepository(db)
        service = GovernmentService(repo)
        return {
            "success": True,
            "data": service.get_global_stats(),
        }
    except Exception as e:
        log.error(f"Error fetching government stats: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/youth-list")
async def get_youth_list(
    current_user: dict = Depends(get_officer_user),
    db=Depends(get_db),
):
    """Returns a list of youth profiles for monitoring."""
    try:
        repo = GovernmentRepository(db)
        service = GovernmentService(repo)
        return {
            "success": True,
            "data": service.get_youth_list(limit=50),
        }
    except Exception as e:
        log.error(f"Error fetching youth list: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
