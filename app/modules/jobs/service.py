"""Jobs service — CRUD business logic."""
from app.modules.jobs.repository import JobsRepository
from app.modules.jobs.schemas import JobCreate, JobUpdate, JobFilter
from app.shared.exceptions import JobNotFound
from app.core.logger import get_logger

log = get_logger("JOBS")


class JobsService:
    def __init__(self, repo: JobsRepository):
        self.repo = repo

    def list_jobs(self, f: JobFilter) -> list[dict]:
        return self.repo.list_jobs(f.state, f.category, f.job_type, f.page, f.limit)

    def get_job(self, job_id: str) -> dict:
        job = self.repo.get_job(job_id)
        if not job:
            raise JobNotFound()
        return job

    def create_job(self, data: JobCreate) -> dict:
        return self.repo.create_job(data.model_dump(exclude_none=True))

    def update_job(self, job_id: str, data: JobUpdate) -> dict:
        job = self.repo.get_job(job_id)
        if not job:
            raise JobNotFound()
        return self.repo.update_job(job_id, data.model_dump(exclude_unset=True)) or job

    def delete_job(self, job_id: str):
        job = self.repo.get_job(job_id)
        if not job:
            raise JobNotFound()
        self.repo.delete_job(job_id)

    def bulk_create(self, jobs: list[JobCreate]) -> int:
        records = [j.model_dump(exclude_none=True) for j in jobs]
        return self.repo.bulk_create(records)
