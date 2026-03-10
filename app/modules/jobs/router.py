"""
Jobs router — public listing + admin CRUD.
Admin routes protected by X-Admin-Secret header via get_admin dependency.
"""
from fastapi import APIRouter, Depends, Query

from app.modules.jobs.service import JobsService
from app.modules.jobs.repository import JobsRepository
from app.modules.jobs.schemas import JobCreate, JobUpdate, JobFilter
from app.shared.dependencies import get_db, get_admin
from app.shared.response_models import ok

router = APIRouter(prefix="/jobs", tags=["jobs"])


def _get_service(db=Depends(get_db)) -> JobsService:
    return JobsService(JobsRepository(db))


# ── Public ─────────────────────────────────────────────────────

@router.get("/")
async def list_jobs(
    state: str | None = Query(None),
    category: str | None = Query(None),
    job_type: str | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, le=100),
    service: JobsService = Depends(_get_service),
):
    f = JobFilter(state=state, category=category, job_type=job_type, page=page, limit=limit)
    return ok(data=service.list_jobs(f))


@router.get("/{job_id}")
async def get_job(job_id: str, service: JobsService = Depends(_get_service)):
    return ok(data=service.get_job(job_id))


# ── Admin ──────────────────────────────────────────────────────

@router.post("/admin/create", dependencies=[Depends(get_admin)])
async def create_job(body: JobCreate, service: JobsService = Depends(_get_service)):
    job = service.create_job(body)
    return ok(data=job, message="Job created.")


@router.patch("/admin/{job_id}", dependencies=[Depends(get_admin)])
async def update_job(job_id: str, body: JobUpdate, service: JobsService = Depends(_get_service)):
    job = service.update_job(job_id, body)
    return ok(data=job, message="Job updated.")


@router.delete("/admin/{job_id}", dependencies=[Depends(get_admin)])
async def delete_job(job_id: str, service: JobsService = Depends(_get_service)):
    service.delete_job(job_id)
    return ok(message="Job deleted.")


@router.post("/admin/bulk", dependencies=[Depends(get_admin)])
async def bulk_create(body: list[JobCreate], service: JobsService = Depends(_get_service)):
    count = service.bulk_create(body)
    return ok(data={"created": count}, message=f"{count} jobs inserted.")
