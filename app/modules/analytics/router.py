from fastapi import APIRouter, Depends, Query, Response
from app.modules.analytics.service import AnalyticsService
from app.modules.analytics.repository import AnalyticsRepository
from app.shared.dependencies import get_db, get_officer_user
from app.shared.response_models import ok
import csv
import io

router = APIRouter(prefix="/analytics", tags=["analytics"])

def _get_service(db=Depends(get_db)) -> AnalyticsService:
    return AnalyticsService(AnalyticsRepository(db))

@router.get("/overview", dependencies=[Depends(get_officer_user)])
async def get_overview(city: str | None = Query(None), service: AnalyticsService = Depends(_get_service)):
    return ok(data=service.get_overview(city))

@router.get("/funnel", dependencies=[Depends(get_officer_user)])
async def get_funnel(city: str | None = Query(None), service: AnalyticsService = Depends(_get_service)):
    return ok(data=service.get_district_funnel(city))

@router.get("/skill-gaps", dependencies=[Depends(get_officer_user)])
async def get_skill_gaps(limit: int = Query(10), city: str | None = Query(None), service: AnalyticsService = Depends(_get_service)):
    return ok(data=service.get_skill_gaps(limit, city))

@router.get("/outcomes", dependencies=[Depends(get_officer_user)])
async def get_outcomes(city: str | None = Query(None), service: AnalyticsService = Depends(_get_service)):
    return ok(data=service.get_training_outcomes(city))

@router.get("/export/csv", dependencies=[Depends(get_officer_user)])
async def export_csv(city: str | None = Query(None), service: AnalyticsService = Depends(_get_service)):
    # Exporting skill gaps as a demonstration
    data = service.get_skill_gaps(limit=1000, city=city) 
    
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["state", "city", "skill_name", "demand", "supply", "gap"])
    writer.writeheader()
    writer.writerows(data)
    
    filename = f"skill_gaps_{city if city else 'national'}.csv"
    
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
