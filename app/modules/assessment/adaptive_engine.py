# OpenAI is used for both question generation and final skill extraction.

import json
from app.modules.assessment.phase_config import (
  get_phase_for_question, get_phase_config
)
from app.core.logger import get_logger

logger = get_logger("ASSESSMENT")

# ── Prompt Templates ─────────────────────────────────────────────
# Defined as module-level constants so they are easy to find,
# read, and update without touching logic code.

QUESTION_SYSTEM_PROMPT = """
You are a skilled career counsellor conducting a career assessment
for India's workforce. You are speaking with a {user_type} from
{state}, with education level: {education_level}.

Current phase: {phase_name}
Phase goal: {phase_goal}

Your instruction for this phase:
{phase_instruction}

Rules you must follow without exception:
- Ask EXACTLY one question. Nothing more, nothing less.
- Keep the question under 25 words.
- Use {language} language only throughout.
- Never repeat or revisit a topic already covered.
- Match vocabulary to education level: {education_level}
- Do not use technical jargon for blue-collar or informal workers.
- The question must sound like a real person asking, not a form field.
- Do not number the question or add any preamble or explanation.

Topics already covered in this conversation: {covered_topics}

Return ONLY this JSON. No other text before or after:
{{
  "question": "the question text here",
  "question_type": "text|mcq|rating",
  "options": ["option1", "option2", "option3"] or null,
  "phase": {phase_number},
  "phase_name": "{phase_name}",
  "skill_probing": "which skill or topic this question targets"
}}

Notes on question_type:
- Use "mcq" when there are 3-4 clear distinct choices
- Use "rating" for questions about confidence or frequency
- Use "text" for open-ended reflective questions
- For "mcq": provide options array with 3-4 short items
- For "rating" and "text": options must be null
"""

SKILL_EXTRACTION_PROMPT = """
You are analyzing completed career assessment responses.
Extract skills and career insights from these question-answer pairs.
Return ONLY valid JSON. No markdown. No preamble. No explanation.

User profile context:
- User type: {user_type}
- Location: {state}
- Education level: {education_level}

All question and answer pairs from the assessment:
{qa_pairs}

Return ONLY this JSON structure:
{{
  "skills": [
    {{
      "skill_name": "skill name relevant to India job market",
      "category": "technical|soft|domain|tool|language",
      "proficiency_numeric": 1,
      "proficiency_label": "Beginner|Elementary|Intermediate|Advanced|Expert",
      "confidence": 0.85,
      "evidence": "exact phrase from answers that shows this skill"
    }}
  ],
  "career_goals": ["goal 1", "goal 2"],
  "blockers": ["main barrier 1", "main barrier 2"],
  "work_preferences": {{
    "environment": "team|solo|mixed",
    "timing": "fixed|flexible",
    "location_flexible": true
  }},
  "assessment_summary": "2 sentence summary of this person career situation"
}}

Proficiency scale:
1=Beginner, 2=Elementary, 3=Intermediate, 4=Advanced, 5=Expert

Important rules:
- Only include skills explicitly mentioned or clearly demonstrated
- Do not infer skills that were never discussed
- Evidence must be a real phrase from the answers, not invented
- assessment_summary must be warm, specific, and encouraging
"""

# ── Helper Functions ─────────────────────────────────────────────

def strip_markdown_fences(text: str) -> str:
  """
  Removes markdown code fences from LLM responses.
  LLMs sometimes wrap JSON in ```json ... ``` despite instructions.
  """
  text = text.strip()
  if text.startswith("```"):
    lines = text.split("\n")
    # Remove first line (```json or ```) and last line (```)
    lines = lines[1:] if lines[0].startswith("```") else lines
    lines = lines[:-1] if lines and lines[-1].strip() == "```" else lines
    text = "\n".join(lines)
  return text.strip()

def extract_covered_topics(conversation_history: list) -> str:
  """
  Scans assistant messages in conversation history and extracts
  the skill_probing field from each question JSON.
  Returns comma-separated string of topics already covered.
  """
  topics = []
  for msg in conversation_history:
    if msg.get("role") == "assistant":
      try:
        content = msg.get("content", "")
        if not content:
          continue
        # Use strip_markdown_fences if needed, but usually content is clean here
        obj = json.loads(content)
        if isinstance(obj, dict) and obj.get("skill_probing"):
          topics.append(str(obj["skill_probing"]))
      except (json.JSONDecodeError, TypeError, KeyError):
        pass
  return ", ".join(topics) if topics else "none yet"

def format_qa_pairs(conversation_history: list) -> str:
  """
  Formats conversation history into readable Q&A text for
  the skill extraction prompt.
  """
  pairs = []
  question_text = None
  for msg in conversation_history:
    if msg.get("role") == "assistant":
      try:
        obj = json.loads(msg["content"])
        question_text = obj.get("question", "")
      except (json.JSONDecodeError, KeyError):
        question_text = msg["content"]
    elif msg.get("role") == "user" and question_text:
      pairs.append(f"Q: {question_text}\nA: {msg['content']}")
      question_text = None
  return "\n\n".join(pairs) if pairs else "No answers recorded."

# ── Core Functions ────────────────────────────────────────────────

async def generate_next_question(
  session: dict,
  user_profile: dict,
  llm_provider
) -> dict:
  """
  Generates the next adaptive question using LLM.
  Reads the full adaptive_context from the session as conversation
  history so each question is informed by all previous answers.

  Args:
    session: current questionnaire_sessions DB record
    user_profile: combined user + profile data dict
    llm_provider: OllamaProvider instance

  Returns:
    Parsed question dict with question, type, options, phase info
  """
  next_q_number = session.get("current_question_number", 0) + 1
  phase_num = get_phase_for_question(next_q_number)
  phase = get_phase_config(phase_num)

  conversation_history = session.get("adaptive_context", [])
  covered_topics = extract_covered_topics(conversation_history)

  # Build system prompt with user context
  system_content = QUESTION_SYSTEM_PROMPT.format(
    user_type=user_profile.get("user_type", "individual"),
    state=user_profile.get("state", "India"),
    education_level=user_profile.get("education_level", "not specified"),
    phase_name=phase["name"],
    phase_goal=phase["goal"],
    phase_instruction=phase["instruction"],
    language="Hindi" if user_profile.get("preferred_lang") == "hi"
             else "English",
    covered_topics=covered_topics,
    phase_number=phase_num
  )

  messages = [{"role": "system", "content": system_content}]
  # Append full conversation history so model has complete context
  messages.extend(conversation_history)

  logger.info(
    f"[ASSESSMENT] Generating Q{next_q_number} for "
    f"user={user_profile.get('user_id')}. "
    f"Phase={phase['name']}. "
    f"History={len(conversation_history)} messages."
  )

  from app.core.llm_config import LLM_TASKS
  from app.schemas.internal.llm_outputs import AssessmentQuestionLLMOutput
  question_raw = await llm_provider.complete_json(
    messages=messages,
    config=LLM_TASKS["assessment"]
  )

  try:
    if not question_raw:
        raise ValueError("Empty response from LLM")
    
    # Validate and heal if needed
    # If phase is missing, we inject it BEFORE validation if possible, 
    # or let the model handle it if we make it optional in the model.
    # Actually, let's just validate and handle errors.
    
    question_model = AssessmentQuestionLLMOutput.model_validate(question_raw)
    question_obj = question_model.model_dump()
    
  except Exception as e:
    logger.error(f"[ASSESSMENT] Failed to validate question JSON: {e}")
    # Fallback healing logic (partially kept from original)
    question_obj = question_raw if question_raw else {}
    
    if "phase" not in question_obj:
      question_obj["phase"] = phase_num
    if "phase_name" not in question_obj:
      question_obj["phase_name"] = phase["name"]
    if "question" not in question_obj or not question_obj["question"]:
      question_obj["question"] = "Can you tell me more about your experience in this field?"
      question_obj["question_type"] = "text"
    if "question_type" not in question_obj:
      question_obj["question_type"] = "text"
    if "skill_probing" not in question_obj:
      question_obj["skill_probing"] = "general experience"

  logger.info(
    f"[ASSESSMENT] Q{next_q_number} generated. "
    f"type={question_obj.get('question_type')}. "
    f"probing={question_obj.get('skill_probing')}"
  )

  return question_obj


async def extract_skills_from_session(
  session: dict,
  user_profile: dict,
  llm_provider
) -> dict:
  """
  Called once after assessment is fully complete.
  Uses LLM for skill extraction.

  Args:
    session: completed questionnaire_sessions record
    user_profile: combined user + profile data dict
    llm_provider: OllamaProvider instance

  Returns:
    Dict with skills list, career_goals, blockers, work_preferences,
    assessment_summary
  """
  conversation_history = session.get("adaptive_context", [])
  qa_pairs = format_qa_pairs(conversation_history)

  prompt = SKILL_EXTRACTION_PROMPT.format(
    user_type=user_profile.get("user_type", "individual"),
    state=user_profile.get("state", "India"),
    education_level=user_profile.get("education_level", "not specified"),
    qa_pairs=qa_pairs
  )

  logger.info(
    f"[ASSESSMENT] Extracting skills from completed session. "
    f"user={user_profile.get('user_id')}. "
    f"QA pairs={qa_pairs.count('Q:')}"
  )

  from app.core.llm_config import LLM_TASKS
  from app.schemas.internal.llm_outputs import SkillExtractionLLMOutput
  extracted_raw = await llm_provider.complete_json(
    messages=[{"role": "user", "content": prompt}],
    config=LLM_TASKS["assessment_extraction"]
  )

  try:
    if not extracted_raw:
        raise ValueError("Empty response from LLM")
    
    extracted_model = SkillExtractionLLMOutput.model_validate(extracted_raw)
    extracted = extracted_model.model_dump()
    
  except Exception as e:
    logger.error(f"[ASSESSMENT] Skill extraction validation failed: {e}")
    # Fallback to empty extraction
    extracted = SkillExtractionLLMOutput().model_dump()

  skills = extracted.get("skills", [])
  logger.info(
    f"[ASSESSMENT] Skills extracted for "
    f"user={user_profile.get('user_id')}. "
    f"count={len(skills)}. "
    f"goals={extracted.get('career_goals', [])}"
  )

  return extracted
