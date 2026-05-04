from app.modules.dashboard.repository import DashboardRepository
from app.modules.ai_chat.providers.ollama_provider import get_ollama_instance
from app.modules.ai_chat.context_builder import build_context_json
from app.modules.jobs.recommendation_engine import JobRecommendationEngine
from app.core.logger import get_logger
import asyncio
import json
import time

log = get_logger("DASHBOARD")

# Fields that count toward profile completion
PROFILE_FIELDS = ["full_name", "age", "gender", "state", "city", "education_level", "languages", "phone"]


class DashboardService:
    def __init__(self, repo: DashboardRepository):
        self.repo = repo
        self.ai_provider = get_ollama_instance()
        self.rec_engine = JobRecommendationEngine(repo.db, self.ai_provider)
        self._insight_cache = {} # {user_id: (timestamp, content)}
        self._job_cache = {} # {user_id: (timestamp, list)}

    async def get_summary(self, user_id: str) -> dict:
        # Fetch basic data in parallel where possible
        user_task = self.repo.get_user(user_id)
        profile_task = self.repo.get_profile(user_id)
        prefs_task = self.repo.get_preferences(user_id)
        
        user, profile, prefs = await asyncio.gather(user_task, profile_task, prefs_task)
        user = user or {}
        profile = profile or {}
        prefs = prefs or {}

        # Profile completion
        filled = [f for f in PROFILE_FIELDS if profile.get(f)]
        completion_pct = int(len(filled) / len(PROFILE_FIELDS) * 100)

        state = profile.get("state", "")
        career_interests = prefs.get("career_interests", [])

        # Fetch skills from user_skill_profiles instead of session
        db = self.repo.db # Using raw supabase client since we need to directly hit tables the repo doesn't map yet
        skills_result = db.table("user_skill_profiles").select(
           "skills"
        ).eq("user_id", user_id).limit(1).execute()
        
        extracted_skills = []
        if skills_result.data and skills_result.data[0].get("skills"):
            for s in skills_result.data[0]["skills"]:
                extracted_skills.append({
                    "name": s.get("skill_name"),
                    "proficiency": s.get("proficiency_label", "Intermediate"),
                    "level": s.get("proficiency_numeric", 2)
                })

        # Check if assessment is done
        assessment_done = user.get("quick_assessment_done", False)
        onboarding_done = user.get("onboarding_done", False)
        nudge_shown = user.get("assessment_nudge_shown", False)

        # Assessment nudge logic:
        # Show nudge if onboarding is done, assessment is NOT done, and nudge hasn't been shown before
        show_nudge = onboarding_done and not assessment_done and not nudge_shown

        # Fetch gap analysis report status
        gap_row = self.repo.db.table("gap_analysis_reports").select(
           "is_stale, computed_at, gaps"
        ).eq("user_id", user_id).limit(1).execute()
        gap_report = gap_row.data[0] if gap_row.data else None
        top_2_gaps = (
           gap_report["gaps"][:2] if gap_report and gap_report.get("gaps") else []
        )

        # Fetch recommended resources based on skill gaps or interests
        target_tags = (top_2_gaps if top_2_gaps else career_interests)
        recommended_courses = await self.repo.get_recommended_resources(target_tags)

        # Fetch enrichment details (primary role, exp)
        enrichment_row = self.repo.db.table("profile_enrichments").select(
           "gemini_extracted, resume_parsed"
        ).eq("user_id", user_id).limit(1).execute()
        
        enrich_data = enrichment_row.data[0] if enrichment_row.data else {}
        # Ensure extracted is ALWAYS a dictionary, even if database fields are null or empty
        raw_extracted = (enrich_data.get("gemini_extracted") or enrich_data.get("resume_parsed") or {})
        extracted = raw_extracted if isinstance(raw_extracted, dict) else {}
        
        log.info(f"Dashboard summary context: user={user_id}, has_enrichment={bool(enrichment_row.data)}, extracted_keys={list(extracted.keys())}")
        
        primary_role = extracted.get("primary_role")
        experience_years = extracted.get("total_experience_years", extracted.get("experience_years"))

        # Check Job Cache (30 min TTL)
        cached_jobs = None
        if user_id in self._job_cache:
            ts, jobs = self._job_cache[user_id]
            if time.time() - ts < 1800:
                cached_jobs = jobs

        # Prepare AI tasks for parallel execution
        ai_tasks = []
        
        # Job matching task
        async def job_task():
            if cached_jobs is not None:
                return cached_jobs
            try:
                jobs = await asyncio.wait_for(
                    self.rec_engine.get_recommendations(user_id, limit=3),
                    timeout=30.0
                )
                self._job_cache[user_id] = (time.time(), jobs)
                return jobs
            except (asyncio.TimeoutError, Exception) as e:
                log.warning(f"Job recommendations failed/timed out: {e}")
                return []

        # AI Insight task
        async def insight_task():
            try:
                return await asyncio.wait_for(
                    self.generate_ai_insight(user, profile, prefs, extracted_skills, top_2_gaps),
                    timeout=10.0
                )
            except (asyncio.TimeoutError, Exception) as e:
                log.warning(f"AI insight failed/timed out: {e}")
                return "Keep growing your skills to unlock new opportunities!"

        # Execute AI tasks in parallel
        job_matches, ai_insight = await asyncio.gather(job_task(), insight_task())


        # Role-specific highlights
        role_specific = {}
        role = user.get("user_type", "individual_youth")

        if role == "individual_youth":
            role_specific = {
                "variant": "student",
                "career_pathways": [
                    {"title": interest, "match_pct": 85} for interest in career_interests[:2]
                ],
                "competitive_exams": await self.repo.get_competitive_exams(profile.get("education_level")),
                "internships": [j for j in job_matches if "intern" in j.get("title", "").lower()]
            }
        elif role == "individual_bluecollar":
            trade = profile.get("primary_trade", "General")
            market_data = await self.repo.get_trade_market_data(trade, state)
            role_specific = {
                "variant": "blue_collar",
                "trade_pulse": market_data or {"demand_level": "Medium", "avg_salary_min": 10000},
                "apprenticeships": [j for j in job_matches if "apprentice" in j.get("title", "").lower()],
                "trade_tips": f"Maintain your tools daily for a 20% longer life, especially for {trade} work."
            }
        elif role == "individual_informal":
            role_specific = {
                "variant": "informal_worker",
                "micro_biz_ideas": [f"Start a {interest} business locally" for interest in career_interests[:2]],
                "govt_schemes": await self.repo.get_government_schemes(state),
                "digital_tips": ["How to use WhatsApp Business", "Finding customers via Google Maps"]
            }

        # (AI tasks handled in parallel above)

        log.debug(f"Computed profile_completion={completion_pct}% for user={user_id}")

        # Fetch recent activities
        recent_activity = await self.repo.get_recent_activities(user_id, limit=5)

        from app.schemas.response.user import UserDashboardResponse, UserProfileResponse

        summary_data = {
            "profile": {
                "id": user_id,
                "email": user.get("email", ""),
                "full_name": profile.get("full_name"),
                "career_stage": role,
                "age": profile.get("age"),
                "gender": profile.get("gender"),
                "state": profile.get("state"),
                "city": profile.get("city"),
                "education_level": profile.get("education_level"),
                "languages": user.get("languages", ["english"]),
                "avatar_url": profile.get("avatar_url"),
                "onboarding_done": onboarding_done,
                "profile_complete_percentage": completion_pct
            },
            "progress_summary": {
                "courses_completed": len([a for a in recent_activity if a["activity_type"] == "course_complete"]),
                "assessments_taken": len([a for a in recent_activity if a["activity_type"] == "assessment_submit"]),
                "skills_verified": len(extracted_skills)
            },
            "top_recommendations": job_matches[:2],
            "notifications_count": 0
        }

        # Validate with Pydantic
        summary_model = UserDashboardResponse.model_validate(summary_data)
        return summary_model.model_dump()

    async def generate_ai_insight(self, user: dict, profile: dict, prefs: dict, skills: list, gaps: list) -> str:
        """Generates a short, punchy AI insight based on user context with caching."""
        user_id = user.get("id")
        
        # 1. Check Cache (1 hour TTL)
        if user_id in self._insight_cache:
            ts, content = self._insight_cache[user_id]
            if time.time() - ts < 3600:
                log.debug(f"Serving cached AI insight for user={user_id}")
                return content

        try:
            # Build context similar to ChatService
            full_data = {
                "user": {k: v for k, v in user.items() if k in ["user_type", "preferred_lang"]},
                "profile": {k: v for k, v in profile.items() if k in ["state", "city", "education_level"]},
                "preferences": prefs,
                "skills": skills[:10], # Limit skills for prompt brevity
                "gaps": gaps[:3]
            }
            context_json = json.dumps(full_data)
            role = user.get("user_type", "individual_youth")
            
            prompt = f"""
            Based on this user context: {context_json}
            
            Role: {role}
            Action: Generate ONE punchy, motivational insight (max 12 words).
            Goal: Suggest a next step based on their skills/gaps.
            Constraint: NO reasoning tags. NO conversational filler. Language: {user.get('preferred_lang', 'en')}
            """
            
            messages = [
                {"role": "system", "content": "You are SkillBridge AI. You give brief, high-impact career tips. Output ONLY the tip."}, 
                {"role": "user", "content": prompt}
            ]
            
            # Use a slightly lower max_tokens and context_window for speed
            response = await self.ai_provider.complete(
                messages, 
                language=user.get("preferred_lang", "en"), 
                max_tokens=40,
                context_window=1024
            )
            
            insight = response.strip().strip('"').strip("'")
            
            # 2. Update Cache
            self._insight_cache[user_id] = (time.time(), insight)
            return insight

        except Exception as e:
            log.error(f"Failed to generate AI insight: {e}")
            return "Keep growing your skills to unlock new opportunities!"

    def mark_nudge_shown(self, user_id: str):
        """Mark that the assessment nudge has been shown to the user once."""
        try:
            self.repo.db.table("users").update({
                "assessment_nudge_shown": True
            }).eq("id", user_id).execute()
            log.info(f"Marked assessment_nudge_shown=True for user={user_id}")
        except Exception as e:
            log.error(f"Failed to mark nudge shown for user={user_id}: {e}")
            raise
