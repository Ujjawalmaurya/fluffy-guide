"""Dashboard router — GET /dashboard/summary."""
from fastapi import APIRouter, Depends

from app.modules.dashboard.service import DashboardService
from app.modules.dashboard.repository import DashboardRepository
from app.schemas.response.user import UserDashboardResponse
from app.shared.dependencies import get_db, get_current_user
from app.shared.response_models import ok, APIResponse

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def _get_service(db=Depends(get_db)) -> DashboardService:
    return DashboardService(DashboardRepository(db))


@router.get("/summary", response_model=APIResponse[UserDashboardResponse])
async def get_summary(
    current_user: dict = Depends(get_current_user),
    service: DashboardService = Depends(_get_service),
):
    summary = await service.get_summary(current_user["id"])
    return ok(data=summary)


@router.post("/nudge-shown", response_model=APIResponse)
async def mark_nudge_shown(
    current_user: dict = Depends(get_current_user),
    service: DashboardService = Depends(_get_service),
):
    service.mark_nudge_shown(current_user["id"])
    return ok(message="Nudge status updated.")
