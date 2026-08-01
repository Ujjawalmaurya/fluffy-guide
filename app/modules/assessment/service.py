import asyncio
import json
from datetime import datetime, timezone, timedelta
from app.modules.assessment.repository import AssessmentRepository
from app.modules.assessment import adaptive_engine
from app.modules.skill_profile import aggregator as skill_aggregator
from app.modules.skill_profile.repository import SkillProfileRepository
from app.modules.ai_chat.providers.base import IStructuredProvider
from app.core.logger import get_logger
from app.core.config import settings
from app.shared.exceptions import AppError

logger = get_logger("ASSESSMENT")

class ASSESSMENT_NO_RETAKES(AppError):
    def __init__(self, next_available_at=None):
        super().__init__("ASSESSMENT_NO_RETAKES", "You have used all your attempts for now.", 403, {"next_available_at": next_available_at})

class ASSESSMENT_SESSION_EXPIRED(AppError):
    def __init__(self):
        super().__init__("ASSESSMENT_SESSION_EXPIRED", "Your assessment session expired due to inactivity. Please start a new one.", 400)

def _utcnow():
    return datetime.now(timezone.utc)

class AssessmentService:
    def __init__(self, repo: AssessmentRepository, llm_provider: IStructuredProvider):
        self.repo = repo
        self.llm_provider = llm_provider

    async def check_retake_eligibility(self, user_id: str) -> dict:
        max_retakes = settings.assessment_max_retakes
        total_allowed = max_retakes + 1
        
        completed_count = await self.repo.get_completed_count(user_id)
        active_session = await self.repo.get_active_session(user_id)
        
        if active_session:
            retakes_used = max(0, completed_count - 1)
            return {
                "eligible": True, "has_incomplete": True, "incomplete_session_id": active_session["id"],
                "retakes_used": retakes_used, "retakes_remaining": max(0, max_retakes - retakes_used),
                "max_retakes": max_retakes, "next_retake_available_at": None
            }
            
        if completed_count >= total_allowed:
            last = await self.repo.get_last_completed(user_id)
            cooldown_hours = settings.assessment_retake_cooldown_hours
            cooldown_expires = None
            if last:
                last_completed_at = last.get("completed_at")
                if isinstance(last_completed_at, str):
                    dt = datetime.fromisoformat(last_completed_at)
                    if dt.tzinfo is None: dt = dt.replace(tzinfo=timezone.utc)
                    last_completed_at = dt
                cooldown_expires = last_completed_at + timedelta(hours=cooldown_hours)
                
            if cooldown_expires and _utcnow() < cooldown_expires:
                return {
                    "eligible": False, "has_incomplete": False, "incomplete_session_id": None,
                    "retakes_used": completed_count, "retakes_remaining": 0,
                    "max_retakes": max_retakes, "next_retake_available_at": cooldown_expires.isoformat()
                }
                
        retakes_used = max(0, completed_count - 1)
        return {
            "eligible": True, "has_incomplete": False, "incomplete_session_id": None,
            "retakes_used": retakes_used, "retakes_remaining": max(0, max_retakes - retakes_used),
            "max_retakes": max_retakes, "next_retake_available_at": None
        }

    async def start_assessment(self, user_id: str, user_profile: dict) -> dict:
        eligibility = await self.check_retake_eligibility(user_id)
        if not eligibility["eligible"]:
            raise ASSESSMENT_NO_RETAKES(next_available_at=eligibility["next_retake_available_at"])
            
        if eligibility["has_incomplete"]:
            session = await self.repo.get_session_by_id(eligibility["incomplete_session_id"], user_id)
            
            # Retrieve the current question from saved adaptive_context if it exists
            batch = None
            for msg in reversed(session.get("adaptive_context", [])):
                if msg.get("role") == "assistant":
                    try:
                        batch = json.loads(msg.get("content", ""))
                        break
                    except (json.JSONDecodeError, TypeError):
                        pass
            
            # Heal legacy single question format if found
            if batch and isinstance(batch, dict):
                if "question" in batch and "questions" not in batch:
                    batch["questions"] = [{
                        "question": batch.pop("question"),
                        "question_type": batch.pop("question_type", "text"),
                        "options": batch.pop("options", []),
                        "allows_multiple": batch.pop("allows_multiple", False),
                        "allows_other": batch.pop("allows_other", True),
                        "skill_probing": batch.pop("skill_probing", "general")
                    }]
                if "questions" in batch and isinstance(batch["questions"], dict):
                    batch["questions"] = [batch["questions"]]
            
            # Fallback: if no active question exists in saved context, generate one
            if not batch:
                batch = await adaptive_engine.generate_next_question(session, {**user_profile, "user_id": user_id}, self.llm_provider)
                await self.repo.update_session(
                    session["id"],
                    adaptive_context=[{"role": "assistant", "content": json.dumps(batch)}],
                    current_question_number=0, last_question_at=_utcnow().isoformat()
                )
                
            return {
                "session_id": session["id"], "batch": batch, "phase": batch.get("phase"),
                "phase_name": batch.get("phase_name"), "question_number": session["current_question_number"] + 1,
                "can_resume": True, **eligibility
            }
            
        completed_count = await self.repo.get_completed_count(user_id)
        session = await self.repo.create_session(user_id=user_id, retake_number=completed_count, max_retakes=settings.assessment_max_retakes)
        
        batch = await adaptive_engine.generate_next_question(session, {**user_profile, "user_id": user_id}, self.llm_provider)
        
        await self.repo.update_session(
            session["id"],
            adaptive_context=[{"role": "assistant", "content": json.dumps(batch)}],
            current_question_number=0, last_question_at=_utcnow().isoformat()
        )
        
        return {
            "session_id": session["id"], "batch": batch, "phase": batch.get("phase"),
            "phase_name": batch.get("phase_name"), "question_number": 1, "can_resume": False, **eligibility
        }

    async def restart_assessment(self, user_id: str) -> dict:
        """Deletes any existing incomplete session quickly from the database."""
        await self.repo.delete_active_session(user_id)
        return {"status": "success"}

    async def submit_answer(self, session_id: str, answer: any, user_id: str, user_profile: dict) -> dict:
        session = await self.repo.get_session_by_id(session_id, user_id)
        if not session: raise ValueError("Session not found")
        if session["is_complete"]: raise ASSESSMENT_SESSION_EXPIRED()
            
        answer_str = json.dumps(answer) if not isinstance(answer, str) else answer
        new_context = session.get("adaptive_context", []) + [{"role": "user", "content": answer_str}]
        
        batch_size = 1
        try:
            parsed = json.loads(answer_str) if isinstance(answer_str, str) else answer_str
            if isinstance(parsed, dict): batch_size = len(parsed)
            elif isinstance(parsed, list): batch_size = max(1, len(parsed))
        except (json.JSONDecodeError, TypeError): batch_size = 1
        
        new_q_number = session["current_question_number"] + batch_size
        max_total = settings.assessment_max_questions
        is_complete = (new_q_number >= max_total)
        
        if is_complete:
            return await self._complete_assessment(session_id, user_id, new_context, user_profile)
            
        # Ensure next batch doesn't exceed total allowed
        remaining = max_total - new_q_number
        
        updated_session = {**session, "adaptive_context": new_context, "current_question_number": new_q_number}
        batch = await adaptive_engine.generate_next_question(updated_session, {**user_profile, "user_id": user_id}, self.llm_provider)
        
        new_context.append({"role": "assistant", "content": json.dumps(batch)})
        await self.repo.update_session(session_id, adaptive_context=new_context, current_question_number=new_q_number, phase=batch.get("phase"), last_question_at=_utcnow().isoformat())
        
        eligibility = await self.check_retake_eligibility(user_id)
        return {
            "session_id": session_id, "batch": batch, "phase": batch.get("phase"),
            "question_number": new_q_number + 1, "is_complete": False, "retakes_remaining": eligibility["retakes_remaining"]
        }

    async def _complete_assessment(self, session_id: str, user_id: str, final_context: list, user_profile: dict) -> dict:
        temp_session = {"adaptive_context": final_context}
        extracted = await adaptive_engine.extract_skills_from_session(temp_session, {**user_profile, "user_id": user_id}, self.llm_provider)
        skills = extracted.get("skills", [])
        summary = extracted.get("assessment_summary", "")
        
        # Pack both verified skills and the structured summary together
        extracted_proficiency_data = {
            "skills": skills,
            "assessment_summary": summary
        }
        
        # Parallelize independent completion tasks
        skill_repo = SkillProfileRepository(self.repo.db)
        await asyncio.gather(
            self.repo.update_session(session_id, is_complete=True, completed_at=_utcnow().isoformat(), adaptive_context=final_context, extracted_proficiency=extracted_proficiency_data),
            skill_aggregator.merge_from_assessment(user_id, skills, skill_repo),
            self.repo.mark_assessment_done(user_id),
            self.repo.invalidate_gap_analysis(user_id),
            self.repo.log_activity(user_id, "assessment_complete", f"Completed AI Assessment with {len(skills)} skills verified.", {"skills_count": len(skills), "session_id": session_id})
        )
        
        eligibility = await self.check_retake_eligibility(user_id)
        return {
            "session_id": session_id, "is_complete": True, "skills_found": skills,
            "career_goals": extracted.get("career_goals", []), "assessment_summary": summary,
            "retakes_remaining": eligibility["retakes_remaining"]
        }

