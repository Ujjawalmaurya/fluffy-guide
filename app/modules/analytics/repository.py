from postgrest import APIResponse

class AnalyticsRepository:
    def __init__(self, db):
        self.db = db

    def get_overview(self, city=None):
        # Using simple aggregate queries for high-level stats
        # For simplicity, we assume user_profiles has city.
        
        # 1. Total users
        total_users_query = self.db.table("user_profiles").select("id", count="exact")
        if city:
            total_users_query = total_users_query.eq("city", city)
        total_users = total_users_query.execute().count or 0
        
        # 2. Active jobs
        job_query = self.db.table("job_listings").select("id", count="exact").eq("is_active", True)
        if city:
            job_query = job_query.eq("location_city", city) # Correct column name from migration 003
        active_jobs = job_query.execute().count or 0
        
        # 3. Onboarded users
        onboarded_query = self.db.table("user_profiles").select("id", count="exact").eq("is_onboarded", True)
        if city:
            onboarded_query = onboarded_query.eq("city", city)
        onboarded_users = onboarded_query.execute().count or 0
        
        return {
            "total_users": total_users,
            "active_jobs": active_jobs,
            "onboarding_rate": (onboarded_users / total_users * 100) if total_users > 0 else 0,
            "completion_rate": 78.5 # Placeholder or calculated if possible
        }

    def get_district_funnel(self, city=None):
        query = self.db.table("district_training_funnel").select("*")
        if city:
            query = query.eq("city", city)
        return query.execute().data

    def get_skill_gaps(self, limit=10, city=None):
        query = self.db.table("skill_gap_by_region").select("*").order("gap", desc=True).limit(limit)
        if city:
            query = query.eq("city", city)
        return query.execute().data

    def get_training_outcomes(self, city=None):
        # If city is provided, filter normally.
        # If not, we might need to aggregate across cities since the view is now regionalized.
        if city:
            query = self.db.table("training_outcomes_monthly").select("month", "completions_count").eq("city", city).order("month")
            return query.execute().data
        else:
            # Aggregate across all regions for the same month
            data = self.db.table("training_outcomes_monthly").select("month", "completions_count").execute().data
            # Manual aggregation since postgrest-python doesn't support complex GROUP BY easily in select()
            aggregated = {}
            for row in data:
                m = row["month"]
                c = row["completions_count"]
                aggregated[m] = aggregated.get(m, 0) + c
            
            result = [{"month": m, "completions_count": c} for m, c in aggregated.items()]
            return sorted(result, key=lambda x: x["month"])
