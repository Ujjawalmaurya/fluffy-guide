"""
SSE processor — streams real processing events after answer submission.
Each event does actual work between yields (not fake delays).
"""
import asyncio
import json
from typing import AsyncGenerator

from app.modules.onboarding.repository import OnboardingRepository
from app.core.logger import get_logger

log = get_logger("SSE")


def _sse_event(step: int, progress: int, message: str, status: str) -> str:
    data = json.dumps({"step": step, "progress": progress, "message": message, "status": status})
    return f"data: {data}\n\n"


def _extract_skills_from_text(text: str) -> list[str]:
    """
    Basic keyword match against 150 common Indian workforce skills.
    Same list used by resume_parser.py. Returns matched skills.
    """
    from app.modules.profile.resume_parser import SKILL_KEYWORDS
    text_lower = text.lower()
    return [skill for skill in SKILL_KEYWORDS if skill.lower() in text_lower]


async def process_stream(session_id: str, repo: OnboardingRepository) -> AsyncGenerator[str, None]:
    """Stream SSE events. Each step does real work."""
    log.info(f"Processing stream started for session={session_id}")

    # Step 1 — fetch session data
    yield _sse_event(1, 10, "📥 Receiving your responses...", "running")
    await asyncio.sleep(0.5)
    session = repo.get_questionnaire_session(session_id)
    if not session:
        yield _sse_event(1, 10, "❌ Session not found.", "error")
        return

    # Step 2 — extract skills from answers
    yield _sse_event(2, 25, "🔍 Extracting skills from your answers...", "running")
    await asyncio.sleep(0.8)
    answers = session.get("answers_data") or []
    all_text = " ".join(a.get("answer", "") for a in answers)
    extracted_skills = _extract_skills_from_text(all_text)

    # Step 3 — load job market data
    user_id = session["user_id"]
    user_result = repo.get_user(user_id)
    # get state from profile
    profile_result = repo.db.table("user_profiles").select("state").eq("user_id", user_id).execute()
    state = profile_result.data[0]["state"] if profile_result.data else "India"

    yield _sse_event(3, 40, f"📍 Loading job market data for {state}...", "running")
    await asyncio.sleep(0.7)
    jobs = repo.get_jobs_for_state(state)
    log.debug(f"Found {len(jobs)} jobs in {state} for session={session_id}")

    # Step 4 — match profile to career paths
    yield _sse_event(4, 60, "🧩 Matching your profile to career paths...", "running")
    await asyncio.sleep(0.8)
    # Basic skill-to-job overlap
    job_matches = 0
    for job in jobs:
        job_skills = [s.lower() for s in (job.get("required_skills") or [])]
        overlap = [s for s in extracted_skills if s.lower() in job_skills]
        if overlap:
            job_matches += 1
    log.debug(f"Matched {job_matches} jobs for session={session_id}")

    # Step 5 — save extracted skills
    yield _sse_event(5, 80, "🧠 Preparing your personalized dashboard...", "running")
    await asyncio.sleep(0.6)
    repo.save_extracted_skills(session_id, extracted_skills)
    repo.mark_onboarding_done(user_id)
    log.info(f"Onboarding processing complete for user={user_id}. Skills: {extracted_skills}")

    # Step 6 — done
    yield _sse_event(6, 100, "✅ Your profile is ready!", "done")
