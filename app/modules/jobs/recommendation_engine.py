import json
from loguru import logger
from app.modules.ai_chat.providers.ollama_provider import OllamaProvider
from app.core import llm_config
from app.modules.dashboard.repository import DashboardRepository
from app.modules.skill_profile.repository import SkillProfileRepository

RANKING_PROMPT = """
You are a career matching AI. Rank these jobs for the user.

User:
- Role: {primary_role}
- Exp: {total_experience_years}y
- Skills: {skills}
- Interests: {interests}
- Loc: {location}

Jobs:
{jobs_json}

Task: Return a JSON array of objects with "id", "match_score" (0-100), and "reason" (max 10 words). 
Format: [{{"id": "...", "match_score": 85, "reason": "..."}}]
Rule: NO reasoning tags. NO conversational text. Raw JSON only.
"""

class JobRecommendationEngine:
    def __init__(self, db, llm_provider: OllamaProvider):
        self.dash_repo = DashboardRepository(db)
        self.skill_repo = SkillProfileRepository(db)
        self.llm_provider = llm_provider

    async def get_recommendations(self, user_id: str, limit: int = 5) -> list[dict]:
        try:
            # 1. Gather Context
            profile = await self.dash_repo.get_profile(user_id)
            prefs = await self.dash_repo.get_preferences(user_id)
            skill_profile = self.skill_repo.get_by_user_id(user_id)
            enrichment = self.dash_repo.db.table("profile_enrichments").select("gemini_extracted").eq("user_id", user_id).execute()
            
            enrich_data = enrichment.data[0] if enrichment.data else {}
            extracted = (enrich_data.get("gemini_extracted") or {})
            
            user_context = {
                "primary_role": extracted.get("primary_role") or profile.get("full_name") or "Professional",
                "total_experience_years": extracted.get("total_experience_years") or 0,
                "skills": [s.get("skill_name", s.get("name")) for s in skill_profile.get("skills", [])] if skill_profile else [],
                "interests": prefs.get("career_interests", []) if prefs else [],
                "location": f"{profile.get('city', '')}, {profile.get('state', '')}" if profile else "India"
            }

            # 2. Pre-filtering (Supabase)
            # Fetch more than we need for the LLM to rank
            state = profile.get("state") if profile else None
            interests = user_context["interests"]
            
            # Simple keyword-based fetch to narrow the pool
            query = self.dash_repo.db.table("job_listings").select("*").eq("is_active", True)
            
            # Try state-specific first
            candidates = []
            if state:
                state_res = query.eq("location_state", state).limit(10).execute()
                candidates = state_res.data or []
            
            # Fallback to general search if no state jobs or state not provided
            if not candidates:
                logger.info(f"[JOB_ENGINE] No state jobs found for {state}. Falling back to national search.")
                national_res = self.dash_repo.db.table("job_listings").select("*").eq("is_active", True).limit(10).execute()
                candidates = national_res.data or []
            
            if not candidates:
                logger.warning("[JOB_ENGINE] No jobs found in database at all.")
                return []

            # 3. Smart Ranking (Ollama)
            jobs_to_rank = [
                {
                    "id": j["id"],
                    "title": j["title"],
                    "company": j["company"],
                    "location_state": j.get("location_state"),
                    "location_city": j.get("location_city"),
                    "required_skills": j.get("required_skills", []),
                    "experience_min": j.get("experience_min", 0),
                    "description": j.get("description", "")[:200] # Provide snippet for context
                }
                for j in candidates
            ]

            formatted_prompt = RANKING_PROMPT.format(
                primary_role=user_context["primary_role"],
                total_experience_years=user_context["total_experience_years"],
                skills=", ".join(user_context["skills"]),
                interests=", ".join(user_context["interests"]),
                location=user_context["location"],
                jobs_json=json.dumps(jobs_to_rank)
            )

            try:
                # Use specific job ranking config
                logger.info(f"[JOB_ENGINE] Ranking {len(jobs_to_rank)} jobs for user={user_id}")
                ranked_data = await self.llm_provider.complete_json(
                    messages=[{"role": "user", "content": formatted_prompt}],
                    config=llm_config.JOB_RANKING
                )
                
                # Ensure ranked_data is a list
                if isinstance(ranked_data, dict):
                    # Sometimes model returns {"rankings": [...]} or similar
                    for key in ["rankings", "jobs", "results", "data"]:
                        if key in ranked_data and isinstance(ranked_data[key], list):
                            ranked_data = ranked_data[key]
                            break
                    if isinstance(ranked_data, dict): # Still a dict?
                        ranked_data = [ranked_data] # Wrap it
                
                if not isinstance(ranked_data, list):
                    logger.warning(f"[JOB_ENGINE] LLM returned non-list data: {type(ranked_data)}. Falling back.")
                    ranked_data = []

            except Exception as e:
                logger.error(f"[JOB_ENGINE] LLM ranking failed: {str(e)}")
                # Fallback to basic scoring if LLM fails
                return await self.dash_repo.get_job_matches(
                    state=state,
                    interests=interests,
                    user_skills=user_context["skills"],
                    limit=limit
                )

            # 4. Merge results
            ranked_lookup = {str(item.get("id")): item for item in ranked_data if isinstance(item, dict) and "id" in item}
            final_recommendations = []
            
            for job in candidates:
                job_id_str = str(job["id"])
                if job_id_str in ranked_lookup:
                    match_info = ranked_lookup[job_id_str]
                    job["match_score"] = match_info.get("match_score", 0)
                    job["reason_for_match"] = match_info.get("reason", "Relevant based on your skills.")
                    final_recommendations.append(job)
                else:
                    # If LLM missed a job but it was in candidates, give it a low score
                    job["match_score"] = 10
                    job["reason_for_match"] = "Found in your region."
                    final_recommendations.append(job)
            
            # Sort by score
            final_recommendations.sort(key=lambda x: x.get("match_score", 0), reverse=True)
            
            return final_recommendations[:limit]

        except Exception as e:
            import traceback
            logger.error(f"[JOB_ENGINE] Critical failure: {str(e)}")
            logger.error(traceback.format_exc())
            return []


