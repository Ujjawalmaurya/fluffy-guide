from app.modules.dashboard.repository import DashboardRepository
from app.modules.ai_chat.providers.base import ILLMProvider
from app.modules.ai_chat.context_builder import build_context_json
from app.modules.jobs.recommendation_engine import JobRecommendationEngine
from app.core.logger import get_logger
from app.core.llm_config import LLM_TASKS
import asyncio
import json
import time

log = get_logger("DASHBOARD")

# Fields that count toward profile completion
PROFILE_FIELDS = ["full_name", "age", "gender", "state", "city", "education_level", "languages", "phone"]

INSIGHT_SYSTEM_PROMPT = """ROLE: You are SkillBridge AI. You give brief, high-impact career tips for India's workforce.
TASK: Generate ONE punchy, motivational insight (max 12 words) for a {role}.
Goal: Suggest a next step based on their skills/gaps.

RULES:
- Output ONLY the tip.
- NO reasoning tags. NO conversational filler.
- Be direct and encouraging.
"""

class DashboardService:
    def __init__(self, repo: DashboardRepository, ai_provider: ILLMProvider):
        self.repo = repo
        self.ai_provider = ai_provider
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


        # Fetch gap analysis report status
        gap_row = self.repo.db.table("gap_analysis_reports").select(
           "is_stale, computed_at, gaps"
        ).eq("user_id", user_id).limit(1).execute()
        gap_report = gap_row.data[0] if gap_row.data else None
        top_2_gaps = (
           gap_report["gaps"][:2] if gap_report and gap_report.get("gaps") else []
        )

        # Fetch recommended resources based on skill gaps or interests.
        # gaps are JSONB dicts {skill_name, priority_score, ...} — extract to plain strings.
        def _to_str_tags(items: list) -> list[str]:
            result = []
            for item in items:
                if isinstance(item, dict):
                    name = item.get("skill_name") or item.get("name") or item.get("skill")
                    if name:
                        result.append(str(name).lower())
                elif isinstance(item, str) and item:
                    result.append(item.lower())
            return result

        raw_tags = top_2_gaps if top_2_gaps else career_interests
        target_tags = _to_str_tags(raw_tags)
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
                "career_stage": profile.get("career_stage") or role,
                "age": profile.get("age"),
                "gender": profile.get("gender"),
                "state": profile.get("state"),
                "city": profile.get("city"),
                "education_level": profile.get("education_level"),
                "languages": profile.get("languages") or user.get("languages") or ["english"],
                "avatar_url": profile.get("avatar_url"),
                "onboarding_done": onboarding_done,
                "profile_complete_percentage": completion_pct
            },
            "ai_highlight": ai_insight,
            "job_matches": job_matches,
            "recommended_courses": recommended_courses,
            "role_specific": role_specific,
            "primary_role": primary_role,
            "experience_years": experience_years,
            "extracted_skills": extracted_skills,
            "quick_assessment_done": assessment_done,
            "recent_activity": recent_activity,
            "progress_summary": {
                "courses_completed": len([a for a in recent_activity if a["activity_type"] == "course_complete"]),
                "assessments_taken": len([a for a in recent_activity if a["activity_type"] == "assessment_submit"]),
                "skills_verified": len(extracted_skills)
            },
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
            system_prompt = INSIGHT_SYSTEM_PROMPT.format(role=role)
            user_prompt = f"USER CONTEXT: {context_json}\n\nGenerate tip now in {user.get('preferred_lang', 'en')}."
            
            messages = [
                {"role": "system", "content": system_prompt}, 
                {"role": "user", "content": user_prompt}
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


    # ── NGO Dashboard Implementation ─────────────────────────────

    async def get_ngo_analytics(self, user_id: str) -> dict:
        """Aggregate analytics for NGO dashboard."""
        # Get linked NGO ID from user profile
        user_profile = await self.repo.db.table("user_profiles").select("linked_org_id").eq("user_id", user_id).single().execute()
        ngo_id = user_profile.data.get("linked_org_id") if user_profile.data else None
        
        stats = await self.repo.get_ngo_stats(ngo_id)
        
        return {
            "total_beneficiaries": stats.get("total_beneficiaries", 0),
            "placed_beneficiaries": stats.get("placed_count", 0),
            "placement_rate": (stats.get("placed_count", 0) / stats.get("total_beneficiaries", 1)) * 100,
            "avg_skill_progress": stats.get("avg_progress", 0),
            "monthly_growth": 12.5 # Still mock, need historical data for this
        }

    async def get_ngo_beneficiaries(self, user_id: str) -> list:
        """Gets real profile summary counts by trade/category for NGO beneficiaries."""
        user_profile = await self.repo.db.table("user_profiles").select("linked_org_id").eq("user_id", user_id).single().execute()
        ngo_id = user_profile.data.get("linked_org_id") if user_profile.data else None
        
        return await self.repo.get_beneficiary_breakdown(ngo_id)

    async def get_ngo_outcomes(self, user_id: str) -> dict:
        user_profile = await self.repo.db.table("user_profiles").select("linked_org_id").eq("user_id", user_id).single().execute()
        ngo_id = user_profile.data.get("linked_org_id") if user_profile.data else None
        stats = await self.repo.get_ngo_stats(ngo_id)
        return {
            "placed": stats.get("placed_count", 0),
            "income_boost": "+25%",
            "completion_rate": f"{stats.get('avg_progress', 0)}%",
            "avg_time_to_place": "50 days"
        }

    async def get_ngo_skill_gaps(self, user_id: str) -> list:
        return await self.repo.get_regional_skill_gaps()

    # ── Government Dashboard Implementation ──────────────────────

    async def get_govt_analytics(self, user_id: str) -> dict:
        # Get user's state if govt official
        profile = await self.repo.get_profile(user_id)
        state = profile.get("state_jurisdiction") if profile else None
        
        stats = await self.repo.get_govt_stats(state=state)
        
        total_users = stats.get('total_users', 0)
        placed_count = stats.get('placed_count', 0)
        
        placement_rate = f"{(placed_count / total_users * 100):.1f}%" if total_users > 0 else "0%"
        
        return {
            "total_users": f"{total_users}",
            "placement_rate": placement_rate,
            "gap_index": "0.45", # Placeholder for complex index
            "revenue": "₹12.5 Cr", # Estimated impact
            "active_jobs": stats.get("active_jobs", 0)
        }

    async def get_govt_placements(self, user_id: str) -> list:
        """Aggregate placements for government view."""
        try:
            profile = await self.repo.get_profile(user_id)
            state = profile.get("state_jurisdiction") if profile else None
            
            placements = await self.repo.get_placements_by_district(state=state)
            
            if not placements:
                # Fallback if no data
                return [
                    {"district": "Indore", "placements": 0, "growth": "0%"},
                    {"district": "Bhopal", "placements": 0, "growth": "0%"}
                ]
            return placements
        except Exception as e:
            log.error(f"Failed to fetch govt placements: {e}")
            return []

    async def get_govt_skill_gaps(self, user_id: str) -> list:
        gaps = await self.repo.get_regional_skill_gaps(limit=5)
        return [{"sector": g["skill"], "gap": f"{20 + g['count']}%", "criticality": g["gap_intensity"]} for g in gaps]

    # ── Talent Matching ──────────────────────────────────────────

    # Industry → candidate user_type/stream/career_interests keyword mapping
    INDUSTRY_CANDIDATE_MAP = {
        "IT & Software":     {"types": ["individual_youth"], "streams": ["Science", "Science & Tech"], "interest_keywords": ["Software Development", "Data Science", "AI/ML", "UI/UX Design", "Digital Marketing"]},
        "Manufacturing":     {"types": ["individual_bluecollar"], "streams": ["Vocational"], "interest_keywords": ["Manufacturing", "Production", "Quality"]},
        "Retail":            {"types": ["individual_youth", "individual_informal"], "streams": ["Commerce", "Commerce & Finance"], "interest_keywords": ["Sales", "Management"]},
        "Healthcare":        {"types": ["individual_youth"], "streams": ["Science"], "interest_keywords": ["Healthcare"]},
        "Construction":      {"types": ["individual_bluecollar"], "streams": ["Vocational"], "interest_keywords": ["Construction", "Electrical", "Plumbing"]},
        "Finance":           {"types": ["individual_youth"], "streams": ["Commerce", "Commerce & Finance"], "interest_keywords": ["Finance", "Accounting", "Management"]},
        "Education":         {"types": ["individual_youth"], "streams": ["Arts", "Science"], "interest_keywords": ["Teaching", "Management"]},
        "Logistics":         {"types": ["individual_bluecollar", "individual_informal"], "streams": ["Vocational", "Other"], "interest_keywords": ["Logistics", "Management"]},
        "Automobile":        {"types": ["individual_bluecollar"], "streams": ["Vocational"], "interest_keywords": ["Automobile", "Manufacturing"]},
        "Other":             {"types": ["individual_youth", "individual_bluecollar", "individual_informal"], "streams": [], "interest_keywords": []},
    }

    async def get_talent_matches(self, employer_id: str, limit: int = 5) -> list:
        """Return candidates that match the employer's industry, roles, and required skills."""
        try:
            db = self.repo.db

            # 1. Fetch the employer's onboarding data from user_profiles
            emp_row = db.table("user_profiles") \
                .select("industry_sector, preferred_skills, roles_hiring_for") \
                .eq("user_id", employer_id).limit(1).execute()
            emp = emp_row.data[0] if emp_row.data else {}

            industry   = emp.get("industry_sector") or "Other"
            req_skills = [s.lower() for s in (emp.get("preferred_skills") or [])]
            roles      = [r.lower() for r in (emp.get("roles_hiring_for") or [])]

            log.info(f"Talent match for employer={employer_id}: industry={industry}, skills={req_skills[:5]}, roles={roles[:5]}")

            # 2. Determine which candidate user_types + streams this industry maps to
            mapping      = self.INDUSTRY_CANDIDATE_MAP.get(industry, self.INDUSTRY_CANDIDATE_MAP["Other"])
            target_types = mapping["types"]
            target_streams      = mapping["streams"]
            interest_keywords   = mapping["interest_keywords"]

            # 3. Fetch candidate profiles filtered by user_type
            type_rows = db.table("users") \
                .select("id") \
                .in_("user_type", target_types) \
                .neq("id", employer_id) \
                .limit(100).execute()
            candidate_ids = [r["id"] for r in (type_rows.data or [])]

            if not candidate_ids:
                log.warning(f"No candidates with types {target_types} found for employer={employer_id}")
                return []

            # 4. Fetch their profiles
            profiles_rows = db.table("user_profiles") \
                .select("user_id, full_name, state, city, education_level, stream, industry_sector") \
                .in_("user_id", candidate_ids).limit(100).execute()
            profile_map = {r["user_id"]: r for r in (profiles_rows.data or [])}

            # 5. Fetch their career interests
            prefs_rows = db.table("user_preferences") \
                .select("user_id, career_interests") \
                .in_("user_id", list(profile_map.keys())).limit(100).execute()
            prefs_map = {r["user_id"]: r.get("career_interests") or [] for r in (prefs_rows.data or [])}

            # 6. Fetch their assessed skills
            skills_rows = db.table("user_skill_profiles") \
                .select("user_id, skills") \
                .in_("user_id", list(profile_map.keys())).limit(100).execute()
            skills_map = {}
            for r in (skills_rows.data or []):
                skills_map[r["user_id"]] = [
                    s.get("skill_name", "").lower()
                    for s in (r.get("skills") or [])
                ]

            # 7. Score each candidate
            scored = []
            for uid, prof in profile_map.items():
                score = 0
                candidate_industry = prof.get("industry_sector")
                candidate_stream = prof.get("stream")

                # STRIKE 1: Industry sector mismatch penalty (VERY HEAVY)
                if industry != "Other" and candidate_industry and candidate_industry != "Other":
                    if industry.lower() != candidate_industry.lower():
                        # Hard block for certain mismatches (IT vs Construction/Manufacturing)
                        if industry == "IT & Software" and candidate_industry in ["Construction", "Manufacturing", "Automobile"]:
                            continue  # Don't even show them
                        score -= 80
                
                # STRIKE 2: Stream match (strong filter for industry fit)
                if target_streams and candidate_stream in target_streams:
                    score += 45
                elif target_streams and candidate_stream:
                    # Penalize if they have a stream that definitely doesn't fit (e.g. Arts for Engineering)
                    score -= 20

                # STRIKE 3: Career interest overlap with industry keywords
                interests = [i.lower() for i in prefs_map.get(uid, [])]
                interest_match = False
                for kw in interest_keywords:
                    if kw.lower() in interests:
                        score += 35
                        interest_match = True
                        break
                
                # If no interest match and it's a specific industry, penalize
                if not interest_match and industry != "Other":
                    score -= 10

                # STRIKE 4: Skill overlap with employer's required skills
                cand_skills = skills_map.get(uid, [])
                if req_skills and cand_skills:
                    overlap = set(req_skills).intersection(set(cand_skills))
                    score += len(overlap) * 40
                
                # Final check: if candidate is explicitly an Electrician/Plumber/Construction worker and it's IT, reject
                if industry == "IT & Software":
                    lowered_skills = [s.lower() for s in cand_skills]
                    lowered_interests = [i.lower() for i in prefs_map.get(uid, [])]
                    
                    # Block Construction/Trade skills
                    trade_skills = ["welding", "electrical", "plumbing", "carpentry", "masonry", "civil engineering"]
                    if any(ts in lowered_skills for ts in trade_skills):
                        log.debug(f"Rejecting candidate {uid} for IT: trade skills found")
                        continue
                        
                    # Block Construction/Trade interests
                    trade_interests = ["electrician", "plumber", "construction", "civil", "trades"]
                    if any(ti in lowered_interests for ti in trade_interests):
                        log.debug(f"Rejecting candidate {uid} for IT: trade interests found")
                        continue

                if score > 25:  # Slightly lower threshold but stricter filters
                    scored.append((score, uid, prof))

            # 8. Sort and return top N
            scored.sort(key=lambda x: x[0], reverse=True)
            top = scored[:limit]

            results = []
            for score, uid, prof in top:
                cand_skills = skills_map.get(uid, [])
                results.append({
                    "id": uid,
                    "name": prof.get("full_name") or "Candidate",
                    "role": ", ".join(prefs_map.get(uid, [])[:2]) or "Skilled Candidate",
                    "match": f"{min(int(score), 100)}%",
                    "location": f"{prof.get('city', '')}, {prof.get('state', '')}".strip(", "),
                    "education": prof.get("education_level"),
                    "top_skills": cand_skills[:3],
                })

            log.info(f"Talent match results for employer={employer_id}: {len(results)} candidates (industry={industry})")
            return results
        except Exception as e:
            log.error(f"Failed to fetch talent matches for employer {employer_id}: {e}")
            return []

    async def get_employer_summary(self, user_id: str) -> dict:
        """Fetch full context for the employer dashboard."""
        try:
            stats_task = self.repo.get_employer_stats(user_id)
            profile_task = self.repo.get_profile(user_id)
            matches_task = self.get_talent_matches(user_id, limit=6)
            
            stats, profile, matches = await asyncio.gather(stats_task, profile_task, matches_task)
            
            # Fetch jobs posted by this employer
            jobs_result = self.repo.db.table("job_listings") \
                .select("*") \
                .eq("employer_id", user_id) \
                .order("created_at", desc=True) \
                .limit(5) \
                .execute()
            
            recent_jobs = jobs_result.data or []

            return {
                "stats": stats,
                "profile": profile or {},
                "talent_matches": matches,
                "recent_jobs": recent_jobs,
                "notifications_count": 0
            }
        except Exception as e:
            log.error(f"Failed to get employer summary for {user_id}: {e}")
            raise
