"""Jobs service — CRUD business logic."""
from typing import List, Dict, Any
from app.modules.jobs.repository import JobsRepository
from app.schemas.request.job import JobCreateRequest, JobUpdateRequest, JobFilterRequest
from app.schemas.response.job import JobResponse
from app.shared.exceptions import JobNotFound
from app.core.logger import get_logger

log = get_logger("JOBS")


class JobsService:
    def __init__(self, repo: JobsRepository):
        self.repo = repo

    def list_jobs(self, f: JobFilterRequest) -> List[Dict[str, Any]]:
        return self.repo.list_jobs(f.state, f.category, f.job_type, f.page, f.limit)

    def get_job(self, job_id: str) -> Dict[str, Any]:
        job = self.repo.get_job(job_id)
        if not job:
            raise JobNotFound()
        return job

    def create_job(self, data: JobCreateRequest) -> Dict[str, Any]:
        return self.repo.create_job(data.model_dump(exclude_none=True))

    def update_job(self, job_id: str, data: JobUpdateRequest) -> Dict[str, Any]:
        job = self.repo.get_job(job_id)
        if not job:
            raise JobNotFound()
        return self.repo.update_job(job_id, data.model_dump(exclude_unset=True)) or job

    def delete_job(self, job_id: str):
        job = self.repo.get_job(job_id)
        if not job:
            raise JobNotFound()
        self.repo.delete_job(job_id)

    def bulk_create(self, jobs: List[JobCreateRequest]) -> int:
        records = [j.model_dump(exclude_none=True) for j in jobs]
        return self.repo.bulk_create(records)
