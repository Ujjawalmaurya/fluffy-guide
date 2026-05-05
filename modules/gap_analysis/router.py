from fastapi import APIRouter, Depends, HTTPException
from typing import List
from pydantic import BaseModel
from .service import GapAnalysisService
from .repository import GapAnalysisRepository, GapAnalysisReport
from .ai_pipeline import GapAnalysisAIPipeline
from .domain import GapAnalysisDomain

router = APIRouter(prefix="/gap-analysis", tags=["Gap Analysis"])

# Dependency Injection
def get_gap_service():
    # In a real app, 'client' would be injected from a database dependency
    repo = GapAnalysisRepository(client=None) 
    ai = GapAnalysisAIPipeline()
    domain = GapAnalysisDomain()
    return GapAnalysisService(repo, ai, domain)

class GapRequest(BaseModel):
    user_id: str
    target_roles: List[str]
    state: str

@router.post("/report")
async def get_gap_report(req: GapRequest, service: GapAnalysisService = Depends(get_gap_service)):
    try:
        report = await service.get_or_compute_report(
            user_id=req.user_id,
            target_roles=req.target_roles,
            state=req.state
        )
        return {
            "success": True,
            "data": report.report_data,
            "meta": {
                "profile_hash": report.profile_hash,
                "user_id": report.user_id
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
