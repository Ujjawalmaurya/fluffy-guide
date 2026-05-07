"""Dashboard repository — joins across profile, preferences, questionnaire, and jobs tables."""
from supabase import Client
from app.core.logger import get_logger

log = get_logger("DASHBOARD")


class DashboardRepository:
    def __init__(self, db: Client):
        self.db = db

    async def get_user(self, user_id: str) -> dict | None:
        result = self.db.table("users").select("*").eq("id", user_id).single().execute()
        return result.data

    async def get_profile(self, user_id: str) -> dict | None:
        result = self.db.table("user_profiles").select("*").eq("user_id", user_id).execute()
        return result.data[0] if result.data else None

    async def get_preferences(self, user_id: str) -> dict | None:
        result = self.db.table("user_preferences").select("*").eq("user_id", user_id).execute()
        return result.data[0] if result.data else None

    async def get_latest_session(self, user_id: str) -> dict | None:
        result = self.db.table("questionnaire_sessions") \
            .select("extracted_skills") \
            .eq("user_id", user_id) \
            .order("created_at", desc=True) \
            .limit(1) \
            .execute()
        return result.data[0] if result.data else None

    async def get_job_matches(self, state: str, interests: list[str], user_skills: list[str] = None, limit: int = 3) -> list[dict]:
        user_skills = user_skills or []
        user_skills_set = {s.lower() for s in user_skills}
        
        # Increase fetch limit to rank a better pool
        query = self.db.table("job_listings") \
            .select("id,title,company,location_city,category,required_skills,salary_min,salary_max") \
            .eq("is_active", True)

        if state:
            query = query.eq("location_state", state)

        result = query.limit(20).execute()
        if not result.data:
            return []

        scored_jobs = []
        for job in result.data:
            score = 0
            title_lower = job.get("title", "").lower()
            job_category = job.get("category", "").lower()
            job_skills = [s.lower() for s in (job.get("required_skills") or [])]
            
            # 1. Category Match (Strong signal)
            if job_category in [i.lower() for i in interests]:
                score += 50
            
            # 2. Skill Overlap (The missing "beat")
            # For each user skill found in job's required skills
            overlap = set(job_skills).intersection(user_skills_set)
            score += len(overlap) * 15  # 15 points per matching skill
            
            # 3. Title Keyword Match
            # If a user's skill appears in the job title (e.g. "Flutter" in "Senior Flutter Developer")
            for skill in user_skills_set:
                if skill in title_lower:
                    score += 25
            
            # Add to list with score
            job["match_score"] = score
            scored_jobs.append(job)

        # Sort by score descending
        scored_jobs.sort(key=lambda x: x["match_score"], reverse=True)
        
        log.info(f"Job matching for skills={user_skills[:3]}...: top_score={scored_jobs[0]['match_score'] if scored_jobs else 0}")
        
        return scored_jobs[:limit]
    async def get_government_schemes(self, state: str = None) -> list[dict]:
        query = self.db.table("government_schemes").select("*").eq("is_active", True)
        if state:
            # Simple check for now, later can use eligibility JSON
            pass
        return query.limit(3).execute().data

    async def get_competitive_exams(self, education_level: str = None) -> list[dict]:
        query = self.db.table("competitive_exams").select("*").eq("is_active", True)
        if education_level:
            query = query.eq("education_level", education_level)
        return query.limit(3).execute().data

    async def get_trade_market_data(self, trade_name: str, state: str) -> dict | None:
        result = self.db.table("trade_market_data") \
            .select("*") \
            .eq("trade_name", trade_name) \
            .eq("state", state) \
            .limit(1) \
            .execute()
        return result.data[0] if result.data else None

    async def get_recommended_resources(self, skill_tags: list, limit: int = 3) -> list[dict]:
        # Normalize: skill_tags may contain dicts (from JSONB gaps) or strings
        def _extract_str(item) -> str | None:
            if isinstance(item, str):
                return item.lower() or None
            if isinstance(item, dict):
                name = item.get("skill_name") or item.get("name") or item.get("skill")
                return str(name).lower() if name else None
            return None

        clean_tags = [s for s in (_extract_str(t) for t in skill_tags) if s]

        if not clean_tags:
            return self.db.table("learning_resources").select("*").limit(limit).execute().data

        result = self.db.table("learning_resources") \
            .select("*") \
            .contains("skill_tags", clean_tags[:3]) \
            .limit(limit) \
            .execute()
        return result.data

    async def log_activity(self, user_id: str, activity_type: str, description: str, metadata: dict = None):
        """Logs a user activity to the database."""
        try:
            self.db.table("user_activities").insert({
                "user_id": user_id,
                "activity_type": activity_type,
                "description": description,
                "metadata": metadata or {}
            }).execute()
        except Exception as e:
            log.error(f"Failed to log activity {activity_type} for user={user_id}: {e}")

    async def get_recent_activities(self, user_id: str, limit: int = 5) -> list[dict]:
        """Fetches the most recent activities for a user."""
        try:
            result = self.db.table("user_activities") \
                .select("*") \
                .eq("user_id", user_id) \
                .order("created_at", desc=True) \
                .limit(limit) \
                .execute()
            return result.data
        except Exception as e:
            log.error(f"Failed to fetch activities for user={user_id}: {e}")
            return []

    async def get_ngo_stats(self, ngo_id: str = None) -> dict:
        """Aggregate stats for NGO dashboard. If ngo_id is provided, filters by NGO's beneficiaries."""
        try:
            if not ngo_id:
                return await self._get_global_ngo_stats()

            # 1. Total Beneficiaries
            query = self.db.table("user_profiles").select("id", count="exact").eq("linked_org_id", ngo_id)
            total = query.execute().count or 0
            
            # 2. Placed Count & 3. Avg Progress via RPCs
            placed = self.db.rpc("get_ngo_placed_count", {"p_ngo_id": ngo_id}).execute()
            placed_count = int(placed.data) if placed.data is not None else 0
            
            progress = self.db.rpc("get_ngo_avg_progress", {"p_ngo_id": ngo_id}).execute()
            avg_progress = float(progress.data) if progress.data is not None else 0.0
            
            return {
                "total_beneficiaries": total,
                "placed_count": placed_count,
                "avg_progress": round(avg_progress, 1)
            }
        except Exception as e:
            log.error(f"Failed to fetch NGO stats for ngo_id={ngo_id}: {e}")
            return await self._get_global_ngo_stats()

    async def _get_global_ngo_stats(self) -> dict:
        """Global fallback for NGO stats when no specific NGO ID is provided."""
        try:
            users_count = self.db.table("users").select("id", count="exact").eq("user_type", "individual_youth").execute().count or 0
            placed_count = self.db.table("user_activities").select("id", count="exact").eq("activity_type", "job_placed").execute().count or 0
            return {
                "total_beneficiaries": users_count,
                "placed_count": placed_count,
                "avg_progress": 68.5
            }
        except Exception as e:
            log.error(f"Error in global NGO stats: {e}")
            return {"total_beneficiaries": 0, "placed_count": 0, "avg_progress": 0}
        except Exception as e:
            log.error(f"Failed to fetch NGO stats: {e}")
            return {}

    async def get_govt_stats(self, state: str = None) -> dict:
        """Aggregate stats for Government dashboard. Filters by state if provided."""
        try:
            # 1. Total Users
            users_query = self.db.table("user_profiles").select("id", count="exact")
            if state:
                users_query = users_query.eq("state", state)
            users_count = users_query.execute().count or 0
            
            # 2. Placements
            if state:
                placed = self.db.rpc("get_state_placed_count", {"p_state": state}).execute()
                placed_count = int(placed.data) if placed.data is not None else 0
            else:
                placed_count = self.db.table("user_activities").select("id", count="exact").eq("activity_type", "job_placed").execute().count or 0

            # 3. Active Job Listings
            jobs_query = self.db.table("job_listings").select("id", count="exact").eq("is_active", True)
            if state:
                jobs_query = jobs_query.eq("location_state", state)
            jobs_count = jobs_query.execute().count or 0
            
            return {
                "total_users": users_count,
                "placed_count": placed_count,
                "active_jobs": jobs_count
            }
        except Exception as e:
            log.error(f"Failed to fetch Govt stats: {e}")
            return {"total_users": 0, "placed_count": 0, "active_jobs": 0}

    async def get_placements_by_district(self, state: str = None) -> list[dict]:
        """Aggregates job_placed activities by city/district."""
        try:
            # We join user_activities with user_profiles
            # Since we can't do complex joins easily in Supabase Python client without RPC,
            # let's assume we have an RPC or do it manually if small.
            # For now, let's use an RPC 'get_placements_by_district'
            result = self.db.rpc("get_placements_by_district", {"p_state": state} if state else {}).execute()
            return result.data if result.data else []
        except Exception as e:
            log.error(f"Error getting placements by district: {e}")
            return []

    async def get_regional_skill_gaps(self, state: str = None, limit: int = 10) -> list[dict]:
        """
        Calculates supply vs demand for skills in a region.
        Supply = Users having the skill in user_skill_profiles.
        Demand = Job listings requiring the skill.
        """
        try:
            params = {"p_state": state} if state else {}
            result = self.db.rpc("get_skill_gaps", params).execute()
            
            if result.data:
                # Format for frontend: [{skill, demand, supply}]
                return result.data[:limit]
            
            return []
        except Exception as e:
            log.error(f"Error getting regional skill gaps: {e}")
            return []

    async def get_beneficiary_breakdown(self, ngo_id: str = None) -> list[dict]:
        """Gets breakdown of beneficiaries by trade/category."""
        try:
            result = self.db.rpc("get_beneficiary_breakdown", {"p_ngo_id": ngo_id} if ngo_id else {}).execute()
            return result.data if result.data else []
        except Exception as e:
            log.error(f"Error getting beneficiary breakdown: {e}")
            return []

    async def get_employer_stats(self, employer_id: str) -> dict:
        """Aggregate stats for Employer dashboard."""
        try:
            # Jobs posted by this employer
            jobs_posted = self.db.table("job_listings").select("id", count="exact").eq("employer_id", employer_id).execute().count or 0
            
            # Total applications received for all jobs by this employer
            # Need to join with job_listings to filter by employer_id
            applications_result = self.db.table("job_applications") \
                .select("id", count="exact") \
                .execute()
            # This is naive, should filter by jobs.employer_id. 
            # In Supabase JS we'd use inner join, in Python it's a bit different.
            # Let's use a simpler approach for now: get all job IDs for this employer first.
            job_ids_result = self.db.table("job_listings").select("id").eq("employer_id", employer_id).execute()
            job_ids = [j['id'] for j in job_ids_result.data]
            
            total_apps = 0
            shortlisted_count = 0
            if job_ids:
                total_apps = self.db.table("job_applications").select("id", count="exact").in_("job_id", job_ids).execute().count or 0
                shortlisted_count = self.db.table("job_applications").select("id", count="exact").in_("job_id", job_ids).eq("status", "shortlisted").execute().count or 0

            return {
                "active_jobs": jobs_posted,
                "total_applicants": total_apps,
                "shortlisted_candidates": shortlisted_count,
                "interviews_scheduled": 0 # Placeholder until we have interviews table
            }
        except Exception as e:
            log.error(f"Failed to fetch employer stats for {employer_id}: {e}")
            return {
                "active_jobs": 0,
                "total_applicants": 0,
                "shortlisted_candidates": 0,
                "interviews_scheduled": 0
            }

    async def get_talent_matches(self, employer_id: str, limit: int = 5) -> list[dict]:
        """Finds relevant candidates for an employer's open roles."""
        try:
            # 1. Get employer's industry sector from their profile
            employer_profile = await self.get_profile(employer_id)
            if not employer_profile:
                return []
            
            employer_industry = employer_profile.get("industry_sector")
            log.info(f"Finding talent matches for employer industry: {employer_industry}")

            # 2. Get all candidate skill profiles
            # Filter by industry sector if possible, or use skills
            # For now, let's get profiles where career_identity or industry_sector matches
            query = self.db.table("user_profiles") \
                .select("user_id, full_name, career_identity, industry_sector, city, education_level, primary_trade, years_experience") \
                .eq("current_work_type", "individual_youth") # Ensure we only get candidates
            
            # If employer has an industry, prioritize candidates in that industry
            # But don't strictly filter if we want "AI" matches across sectors
            # Actually, the user complained about "Electricians" in "IT Sector".
            # So we SHOULD filter or heavily penalize cross-sector mismatches.
            
            result = query.limit(50).execute()
            if not result.data:
                return []

            # 3. Get candidate skills from their skill profiles
            candidates = result.data
            candidate_ids = [c["user_id"] for c in candidates]
            
            skills_result = self.db.table("user_skill_profiles") \
                .select("user_id, top_skills") \
                .in_("user_id", candidate_ids) \
                .execute()
            
            skills_map = {s["user_id"]: (s["top_skills"] or []) for s in skills_result.data}

            scored_candidates = []
            for c in candidates:
                uid = c["user_id"]
                candidate_industry = c.get("industry_sector")
                candidate_skills = [s.lower() for s in skills_map.get(uid, [])]
                
                score = 0
                
                # Industry Match (Crucial to prevent Electricians in IT)
                if employer_industry and candidate_industry:
                    if employer_industry.lower() == candidate_industry.lower():
                        score += 100
                    else:
                        # Heavy penalty for industry mismatch if both have sectors defined
                        score -= 50
                
                # Keyword matching (e.g. "AI", "Cloud", "Plumbing")
                # This helps if industries aren't perfectly aligned but skills are
                if employer_industry:
                    emp_ind_lower = employer_industry.lower()
                    if emp_ind_lower in (c.get("career_identity") or "").lower():
                        score += 50
                    
                    for skill in candidate_skills:
                        if skill in emp_ind_lower or emp_ind_lower in skill:
                            score += 30

                c["match_score"] = score
                c["top_skills"] = skills_map.get(uid, [])
                scored_candidates.append(c)

            # Sort and filter
            scored_candidates.sort(key=lambda x: x["match_score"], reverse=True)
            
            # Filter out very low scores to ensure relevance
            relevant_candidates = [c for c in scored_candidates if c["match_score"] > 0]
            
            return relevant_candidates[:limit]

        except Exception as e:
            log.error(f"Failed to fetch talent matches for employer {employer_id}: {e}")
            return []
