# [ASSESSMENT] Pydantic v2 request and response models.
# Every endpoint input and output is typed here.

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class SubmitAnswerRequest(BaseModel):
  session_id: str = Field(..., description="Active session ID")
  answer: str = Field(
    ..., min_length=1,
    description="User answer to current question"
  )

class QuestionResponse(BaseModel):
  question: str
  question_type: str    # "text" | "mcq" | "rating"
  options: Optional[list[str]] = None
  phase: int
  phase_name: str
  skill_probing: str

class StartAssessmentResponse(BaseModel):
  session_id: str
  question: QuestionResponse
  phase: int
  phase_name: str
  question_number: int
  retakes_used: int
  retakes_remaining: int
  max_retakes: int
  can_resume: bool      # True if returning to incomplete session

class AnswerResponse(BaseModel):
  session_id: str
  question: Optional[QuestionResponse] = None
  phase: int
  question_number: int
  is_complete: bool
  retakes_remaining: int
  # Populated only when is_complete=True
  skills_found: Optional[list] = None
  career_goals: Optional[list[str]] = None
  assessment_summary: Optional[str] = None

class AssessmentStatusResponse(BaseModel):
  has_completed: bool
  retakes_used: int
  retakes_remaining: int
  max_retakes: int
  last_completed_at: Optional[datetime] = None
  can_retake: bool
  next_retake_available_at: Optional[datetime] = None
  has_incomplete: bool
  incomplete_session_id: Optional[str] = None

class AssessmentHistoryItem(BaseModel):
  session_id: str
  retake_number: int
  is_complete: bool
  completed_at: Optional[datetime]
  skills_count: int
  created_at: datetime
