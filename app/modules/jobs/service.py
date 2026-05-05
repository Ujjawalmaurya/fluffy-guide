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
        return self.repo.list_jobs(f.state, f.category, f.job_type, f.query, f.page, f.limit)

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

    def get_my_postings(self, user_id: str) -> List[Dict[str, Any]]:
        return self.repo.get_my_postings(user_id)

    async def create_employer_job(self, user_id: str, data: JobCreateRequest) -> Dict[str, Any]:
        job_data = data.model_dump(exclude_none=True)
        
        # 1. Fetch employer profile to fill missing defaults
        profile_row = self.repo.db.table("user_profiles").select(
            "full_name, industry_sector, state"
        ).eq("user_id", user_id).limit(1).execute()
        profile = profile_row.data[0] if profile_row.data else {}

        # 2. Fill missing fields
        if not job_data.get("company"):
            job_data["company"] = profile.get("full_name") or "Our Company"
        
        if not job_data.get("category"):
            job_data["category"] = profile.get("industry_sector") or "General"
        
        if not job_data.get("location_state"):
            job_data["location_state"] = profile.get("state") or "India"

        # 3. Handle salary string if numeric ones are missing
        if job_data.get("salary") and not job_data.get("salary_min"):
            try:
                # Basic string cleaning for "27000" or "₹27,000"
                clean_salary = "".join(filter(str.isdigit, str(job_data["salary"])))
                if clean_salary:
                    job_data["salary_min"] = int(clean_salary)
            except:
                pass
        
        # Clean up the extra 'salary' field before repo call
        if "salary" in job_data:
            del job_data["salary"]

        job_data["employer_id"] = user_id
        return self.repo.create_job(job_data)
