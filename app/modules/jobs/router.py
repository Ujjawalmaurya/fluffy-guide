"""
Jobs router — public listing + admin CRUD.
Admin routes protected by X-Admin-Secret header via get_admin dependency.
"""
from typing import List
from fastapi import APIRouter, Depends, Query

from app.modules.jobs.service import JobsService
from app.modules.jobs.repository import JobsRepository
from app.schemas.request.job import JobCreateRequest, JobUpdateRequest, JobFilterRequest
from app.schemas.response.job import JobResponse
from app.schemas.enums import JobType
from app.shared.dependencies import get_db, get_admin
from app.shared.response_models import ok, APIResponse

router = APIRouter(prefix="/jobs", tags=["jobs"])


def _get_service(db=Depends(get_db)) -> JobsService:
    return JobsService(JobsRepository(db))


# ── Public ─────────────────────────────────────────────────────

@router.get("/", response_model=APIResponse[List[JobResponse]])
async def list_jobs(
    state: str | None = Query(None),
    category: str | None = Query(None),
    job_type: JobType | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, le=100),
    service: JobsService = Depends(_get_service),
):
    f = JobFilterRequest(state=state, category=category, job_type=job_type, page=page, limit=limit)
    return ok(data=service.list_jobs(f))


@router.get("/{job_id}", response_model=APIResponse[JobResponse])
async def get_job(job_id: str, service: JobsService = Depends(_get_service)):
    return ok(data=service.get_job(job_id))


# ── Admin ──────────────────────────────────────────────────────

@router.post("/admin/create", response_model=APIResponse[JobResponse], dependencies=[Depends(get_admin)])
async def create_job(body: JobCreateRequest, service: JobsService = Depends(_get_service)):
    job = service.create_job(body)
    return ok(data=job, message="Job created.")


@router.patch("/admin/{job_id}", response_model=APIResponse[JobResponse], dependencies=[Depends(get_admin)])
async def update_job(job_id: str, body: JobUpdateRequest, service: JobsService = Depends(_get_service)):
    job = service.update_job(job_id, body)
    return ok(data=job, message="Job updated.")


@router.delete("/admin/{job_id}", response_model=APIResponse, dependencies=[Depends(get_admin)])
async def delete_job(job_id: str, service: JobsService = Depends(_get_service)):
    service.delete_job(job_id)
    return ok(message="Job deleted.")


@router.post("/admin/bulk", response_model=APIResponse, dependencies=[Depends(get_admin)])
async def bulk_create(body: List[JobCreateRequest], service: JobsService = Depends(_get_service)):
    count = service.bulk_create(body)
    return ok(data={"created": count}, message=f"{count} jobs inserted.")
