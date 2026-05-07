"""Dashboard router — GET /dashboard/summary."""
from fastapi import APIRouter, Depends

from app.modules.dashboard.service import DashboardService
from app.modules.dashboard.repository import DashboardRepository
from app.schemas.response.user import UserDashboardResponse
from app.shared.dependencies import get_db, get_current_user, require_user_type, get_llm_provider
from app.shared.response_models import ok, APIResponse

router = APIRouter(tags=["dashboard"])


def _get_service(
    db=Depends(get_db), 
    provider=Depends(get_llm_provider)
) -> DashboardService:
    return DashboardService(DashboardRepository(db), provider)


@router.get("/dashboard/summary", response_model=APIResponse[UserDashboardResponse])
async def get_summary(
    current_user: dict = Depends(get_current_user),
    service: DashboardService = Depends(_get_service),
):
    summary = await service.get_summary(current_user["id"])
    return ok(data=summary)




# ── NGO Dashboard ──────────────────────────────────────────────

@router.get("/ngo/beneficiaries", response_model=APIResponse)
async def get_ngo_beneficiaries(
    current_user: dict = Depends(require_user_type(["org_ngo"])),
    service: DashboardService = Depends(_get_service),
):
    data = await service.get_ngo_beneficiaries(current_user["id"])
    return ok(data=data)


@router.get("/ngo/outcomes", response_model=APIResponse)
async def get_ngo_outcomes(
    current_user: dict = Depends(require_user_type(["org_ngo"])),
    service: DashboardService = Depends(_get_service),
):
    data = await service.get_ngo_outcomes(current_user["id"])
    return ok(data=data)


@router.get("/ngo/skill-gaps", response_model=APIResponse)
async def get_ngo_skill_gaps(
    current_user: dict = Depends(require_user_type(["org_ngo"])),
    service: DashboardService = Depends(_get_service),
):
    data = await service.get_ngo_skill_gaps(current_user["id"])
    return ok(data=data)


# ── Government Dashboard ───────────────────────────────────────

@router.get("/govt/analytics", response_model=APIResponse)
async def get_govt_analytics(
    current_user: dict = Depends(require_user_type(["org_govt"])),
    service: DashboardService = Depends(_get_service),
):
    data = await service.get_govt_analytics(current_user["id"])
    return ok(data=data)


@router.get("/govt/placements", response_model=APIResponse)
async def get_govt_placements(
    current_user: dict = Depends(require_user_type(["org_govt"])),
    service: DashboardService = Depends(_get_service),
):
    data = await service.get_govt_placements(current_user["id"])
    return ok(data=data)


@router.get("/govt/skill-gaps", response_model=APIResponse)
async def get_govt_skill_gaps(
    current_user: dict = Depends(require_user_type(["org_govt"])),
    service: DashboardService = Depends(_get_service),
):
    data = await service.get_govt_skill_gaps(current_user["id"])
    return ok(data=data)


# ── Talent Matching ───────────────────────────────────────────

@router.get("/talent/matches", response_model=APIResponse)
async def get_talent_matches(
    current_user: dict = Depends(require_user_type(["org_employer", "org_govt"])),
    service: DashboardService = Depends(_get_service),
):
    data = await service.get_talent_matches(current_user["id"])
    return ok(data=data)
