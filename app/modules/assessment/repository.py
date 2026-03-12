# [ASSESSMENT] Database queries for assessment module.
# No business logic here — only DB operations.
# All queries use the Supabase client from app/core/database.py

from app.core.database import get_supabase
from app.core.logger import get_logger

logger = get_logger("ASSESSMENT")

async def create_session(
  user_id: str,
  retake_number: int,
  max_retakes: int
) -> dict:
  """Creates a new questionnaire_sessions record for quick_assessment."""
  supabase = get_supabase()
  result = supabase.table("questionnaire_sessions").insert({
    "user_id": user_id,
    "assessment_type": "quick_assessment",
    "retake_number": retake_number,
    "max_retakes": max_retakes,
    "phase": 1,
    "current_question_number": 0,
    "adaptive_context": [],
    "extracted_proficiency": [],
    "is_complete": False,
    "language": "en"
  }).execute()
  logger.debug(
    f"[ASSESSMENT] Session created. user={user_id}. "
    f"retake={retake_number}"
  )
  return result.data[0]

async def get_active_session(user_id: str) -> dict | None:
  """
  Returns the most recent INCOMPLETE quick_assessment session.
  Used to detect if user has an unfinished assessment to resume.
  """
  supabase = get_supabase()
  result = (
    supabase.table("questionnaire_sessions")
    .select("*")
    .eq("user_id", user_id)
    .eq("assessment_type", "quick_assessment")
    .eq("is_complete", False)
    .order("created_at", desc=True)
    .limit(1)
    .execute()
  )
  return result.data[0] if result.data else None

async def get_session_by_id(
  session_id: str,
  user_id: str
) -> dict | None:
  """
  Fetches a session by ID. user_id check prevents accessing
  other users sessions — always pass current user's ID.
  """
  supabase = get_supabase()
  result = (
    supabase.table("questionnaire_sessions")
    .select("*")
    .eq("id", session_id)
    .eq("user_id", user_id)
    .limit(1)
    .execute()
  )
  return result.data[0] if result.data else None

async def update_session(session_id: str, **fields) -> dict:
  """
  Updates any subset of fields on a session record.
  Called after each answer is submitted and after completion.
  """
  supabase = get_supabase()
  result = (
    supabase.table("questionnaire_sessions")
    .update(fields)
    .eq("id", session_id)
    .execute()
  )
  return result.data[0]

async def get_completed_count(user_id: str) -> int:
  """
  Returns count of completed quick_assessment sessions.
  Used to determine how many attempts the user has used.
  """
  supabase = get_supabase()
  result = (
    supabase.table("questionnaire_sessions")
    .select("id", count="exact")
    .eq("user_id", user_id)
    .eq("assessment_type", "quick_assessment")
    .eq("is_complete", True)
    .execute()
  )
  return result.count or 0

async def get_last_completed(user_id: str) -> dict | None:
  """
  Returns the most recently completed quick_assessment session.
  Used for retake cooldown calculation.
  """
  supabase = get_supabase()
  result = (
    supabase.table("questionnaire_sessions")
    .select("*")
    .eq("user_id", user_id)
    .eq("assessment_type", "quick_assessment")
    .eq("is_complete", True)
    .order("completed_at", desc=True)
    .limit(1)
    .execute()
  )
  return result.data[0] if result.data else None

async def get_history(user_id: str) -> list:
  """
  Returns all quick_assessment sessions for a user, newest first.
  Returns summary fields only — not full adaptive_context.
  """
  supabase = get_supabase()
  result = (
    supabase.table("questionnaire_sessions")
    .select(
      "id, retake_number, is_complete, completed_at, "
      "extracted_proficiency, current_question_number, created_at"
    )
    .eq("user_id", user_id)
    .eq("assessment_type", "quick_assessment")
    .order("created_at", desc=True)
    .execute()
  )
  return result.data or []
