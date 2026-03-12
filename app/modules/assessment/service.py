# [ASSESSMENT] Business logic for assessment flow.
# Coordinates between repository, adaptive_engine, and
# skill_profile aggregator.
# Never contains direct DB queries — all DB goes via repository.

import json
from datetime import datetime, timedelta, timezone
from app.modules.assessment import repository, adaptive_engine
from app.modules.assessment.phase_config import get_phase_for_question
from app.modules.skill_profile import aggregator as skill_aggregator
from app.modules.skill_profile.repository import SkillProfileRepository
from app.core.database import get_supabase
from app.core.logger import get_logger
from app.core.config import settings
from app.shared.exceptions import (
    OpenAIRateLimit, GeminiRateLimit, GeminiParseError, AppError
)

logger = get_logger("ASSESSMENT")

# Quick definition for exception classes specific to this service
class ASSESSMENT_NO_RETAKES(AppError):
    def __init__(self, next_available_at=None):
        super().__init__("ASSESSMENT_NO_RETAKES", "You have used all your attempts for now.", 403, {"next_available_at": next_available_at})

class ASSESSMENT_SESSION_EXPIRED(AppError):
    def __init__(self):
        super().__init__("ASSESSMENT_SESSION_EXPIRED", "Your assessment session expired due to inactivity. Please start a new one.", 400)


def _utcnow():
    return datetime.now(timezone.utc)

async def check_retake_eligibility(user_id: str) -> dict:
    """
    Checks if user can start or retake an assessment.
    Returns full eligibility state used by both /start and /retake.
    Total allowed attempts = max_retakes + 1
    (The first attempt is not a retake.)
    """
    max_retakes = settings.assessment_max_retakes
    total_allowed = max_retakes + 1
    
    completed_count = await repository.get_completed_count(user_id)
    active_session = await repository.get_active_session(user_id)
    
    # If there is an active incomplete session, always allow resuming
    if active_session:
        retakes_used = max(0, completed_count - 1)
        return {
            "eligible": True,
            "has_incomplete": True,
            "incomplete_session_id": active_session["id"],
            "retakes_used": retakes_used,
            "retakes_remaining": max(0, max_retakes - retakes_used),
            "max_retakes": max_retakes,
            "next_retake_available_at": None
        }
        
    # Check if all attempts used
    if completed_count >= total_allowed:
        last = await repository.get_last_completed(user_id)
        cooldown_hours = settings.assessment_retake_cooldown_hours
        
        cooldown_expires = None
        if last:
            # handle timezone offsets if needed, assuming iso dict contains str format
            last_completed_at = last.get("completed_at")
            if isinstance(last_completed_at, str):
                dt = datetime.fromisoformat(last_completed_at)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                last_completed_at = dt
            cooldown_expires = last_completed_at + timedelta(hours=cooldown_hours)
            
        if cooldown_expires and _utcnow() < cooldown_expires:
            logger.info(
                f"[ASSESSMENT] No retakes remaining for user={user_id}. "
                f"Next available: {cooldown_expires}"
            )
            return {
                "eligible": False,
                "has_incomplete": False,
                "incomplete_session_id": None,
                "retakes_used": completed_count,
                "retakes_remaining": 0,
                "max_retakes": max_retakes,
                "next_retake_available_at": cooldown_expires.isoformat()
            }
            
    retakes_used = max(0, completed_count - 1)
    return {
        "eligible": True,
        "has_incomplete": False,
        "incomplete_session_id": None,
        "retakes_used": retakes_used,
        "retakes_remaining": max(0, max_retakes - retakes_used),
        "max_retakes": max_retakes,
        "next_retake_available_at": None
    }


async def start_assessment(
    user_id: str,
    user_profile: dict,
    openai_provider,
    gemini_provider
) -> dict:
    """
    Starts a new assessment or resumes an existing incomplete one.
    Returns first question + session metadata.
    """
    eligibility = await check_retake_eligibility(user_id)
    if not eligibility["eligible"]:
        raise ASSESSMENT_NO_RETAKES(
            next_available_at=eligibility["next_retake_available_at"]
        )
        
    # Resume incomplete session if one exists
    if eligibility["has_incomplete"]:
        session = await repository.get_session_by_id(
            eligibility["incomplete_session_id"], user_id
        )
        
        # Re-generate the question for the current position
        question = await adaptive_engine.generate_next_question(
            session, {**user_profile, "user_id": user_id}, openai_provider
        )
        logger.info(
            f"[ASSESSMENT] Resuming session for user={user_id}. "
            f"Q={session['current_question_number'] + 1}"
        )
        return {
            "session_id": session["id"],
            "question": question,
            "phase": question["phase"],
            "phase_name": question["phase_name"],
            "question_number": session["current_question_number"] + 1,
            "can_resume": True,
            **eligibility
        }
        
    # Create new session
    completed_count = await repository.get_completed_count(user_id)

    session = await repository.create_session(
        user_id=user_id,
        retake_number=completed_count,
        max_retakes=settings.assessment_max_retakes
    )
    
    logger.info(
        f"[ASSESSMENT] New session started. user={user_id}. "
        f"attempt={completed_count + 1}/{settings.assessment_max_retakes + 1}"
    )
    
    question = await adaptive_engine.generate_next_question(
        session, {**user_profile, "user_id": user_id}, openai_provider
    )
    
    # Save first question to adaptive_context
    await repository.update_session(
        session["id"],
        adaptive_context=[{
            "role": "assistant",
            "content": json.dumps(question)
        }],
        current_question_number=1,
        last_question_at=_utcnow().isoformat()
    )
    
    return {
        "session_id": session["id"],
        "question": question,
        "phase": question["phase"],
        "phase_name": question["phase_name"],
        "question_number": 1,
        "can_resume": False,
        **eligibility
    }


async def submit_answer(
    session_id: str,
    answer: str,
    user_id: str,
    user_profile: dict,
    openai_provider,
    gemini_provider
) -> dict:
    """
    Accepts user answer, appends to context, generates next question
    OR completes the assessment if max questions reached.
    """
    session = await repository.get_session_by_id(session_id, user_id)
    if not session:
        raise ValueError("Session not found or does not belong to user")
        
    if session["is_complete"]:
        raise ASSESSMENT_SESSION_EXPIRED()
        
    # Check session timeout (2 hours of inactivity)
    if session.get("last_question_at"):
        last_activity_str = str(session["last_question_at"])
        # Support python 3.10 standard iso format parsing 
        last_activity = datetime.fromisoformat(last_activity_str.replace('Z', '+00:00'))
        if last_activity.tzinfo is None:
            last_activity = last_activity.replace(tzinfo=timezone.utc)
            
        if _utcnow() - last_activity > timedelta(hours=2):
            logger.info(
                f"[ASSESSMENT] Session expired due to inactivity. "
                f"session={session_id}"
            )
            raise ASSESSMENT_SESSION_EXPIRED()
            
    # Append user answer to conversation context
    new_context = session.get("adaptive_context", []) + [
        {"role": "user", "content": answer}
    ]
    
    new_q_number = session["current_question_number"] + 1
    is_complete = (new_q_number > settings.assessment_max_questions)
    
    logger.info(
        f"[ASSESSMENT] Q{session['current_question_number']} answered. "
        f"user={user_id}. next_q={new_q_number}. "
        f"is_complete={is_complete}"
    )
    
    if is_complete:
        return await _complete_assessment(
            session_id, user_id, new_context, user_profile, gemini_provider
        )
        
    # Generate next question
    updated_session = {
        **session,
        "adaptive_context": new_context,
        "current_question_number": new_q_number
    }
    
    question = await adaptive_engine.generate_next_question(
        updated_session,
        {**user_profile, "user_id": user_id},
        openai_provider
    )
    
    new_context.append({
        "role": "assistant",
        "content": json.dumps(question)
    })
    
    await repository.update_session(
        session_id,
        adaptive_context=new_context,
        current_question_number=new_q_number,
        phase=question["phase"],
        last_question_at=_utcnow().isoformat()
    )
    
    eligibility = await check_retake_eligibility(user_id)
    return {
        "session_id": session_id,
        "question": question,
        "phase": question["phase"],
        "question_number": new_q_number,
        "is_complete": False,
        "retakes_remaining": eligibility["retakes_remaining"]
    }


async def _complete_assessment(
    session_id: str,
    user_id: str,
    final_context: list,
    user_profile: dict,
    gemini_provider
) -> dict:
    """
    Internal: finalizes assessment, extracts skills, updates profile.
    Called from submit_answer when max questions reached.
    """
    # Build temp session dict for extraction
    temp_session = {"adaptive_context": final_context}
    
    extracted = await adaptive_engine.extract_skills_from_session(
        temp_session,
        {**user_profile, "user_id": user_id},
        gemini_provider
    )
    
    skills = extracted.get("skills", [])
    
    # Mark session complete
    await repository.update_session(
        session_id,
        is_complete=True,
        completed_at=_utcnow().isoformat(),
        adaptive_context=final_context,
        extracted_proficiency=skills
    )
    
    # Merge skills into user_skill_profiles
    skill_repo = SkillProfileRepository(get_supabase())
    await skill_aggregator.merge_from_assessment(user_id, skills, skill_repo)

    # Update users.quick_assessment_done
    db = get_supabase()
    db.table("users").update(
        {"quick_assessment_done": True}
    ).eq("id", user_id).execute()

    # Mark gap analysis as stale (profile changed)
    db.table("gap_analysis_reports").update(
        {"is_stale": True}
    ).eq("user_id", user_id).execute()
    
    logger.info(
        f"[ASSESSMENT] Completed for user={user_id}. "
        f"skills={len(skills)}. "
        f"goals={extracted.get('career_goals', [])}"
    )
    
    eligibility = await check_retake_eligibility(user_id)
    return {
        "session_id": session_id,
        "is_complete": True,
        "skills_found": skills,
        "career_goals": extracted.get("career_goals", []),
        "assessment_summary": extracted.get("assessment_summary", ""),
        "retakes_remaining": eligibility["retakes_remaining"]
    }
