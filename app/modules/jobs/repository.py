"""Jobs repository — all DB ops for job_listings table."""
from supabase import Client
from app.core.logger import get_logger

log = get_logger("JOBS")


class JobsRepository:
    def __init__(self, db: Client):
        self.db = db

    def list_jobs(self, state: str | None, category: str | None, job_type: str | None, page: int, limit: int) -> list[dict]:
        query = self.db.table("job_listings").select("*").eq("is_active", True)
        if state:
            query = query.eq("location_state", state)
        if category:
            query = query.eq("category", category)
        if job_type:
            query = query.eq("job_type", job_type)
        offset = (page - 1) * limit
        result = query.range(offset, offset + limit - 1).execute()
        return result.data or []

    def get_job(self, job_id: str) -> dict | None:
        result = self.db.table("job_listings").select("*").eq("id", job_id).single().execute()
        return result.data

    def create_job(self, data: dict) -> dict:
        result = self.db.table("job_listings").insert(data).execute()
        log.info(f"Job created: {data.get('title')} @ {data.get('company')}")
        return result.data[0]

    def update_job(self, job_id: str, data: dict) -> dict | None:
        clean = {k: v for k, v in data.items() if v is not None}
        result = self.db.table("job_listings").update(clean).eq("id", job_id).execute()
        return result.data[0] if result.data else None

    def delete_job(self, job_id: str):
        # soft delete
        self.db.table("job_listings").update({"is_active": False}).eq("id", job_id).execute()
        log.info(f"Job soft-deleted: id={job_id}")

    def bulk_create(self, jobs: list[dict]) -> int:
        result = self.db.table("job_listings").insert(jobs).execute()
        count = len(result.data) if result.data else 0
        log.info(f"Bulk insert: {count} jobs added by admin")
        return count
