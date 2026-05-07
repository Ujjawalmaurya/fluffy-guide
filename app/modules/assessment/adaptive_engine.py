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
- Generate EXACTLY {batch_size} distinct questions.
- Each question must be under 20 words.
- Provide 3-8 short, predictable answer chips for each question.
- Set "allows_multiple" to true if user can reasonably select multiple options.
- "allows_other" should usually be true.
- Use {language} language only throughout.
- Never repeat or revisit a topic already covered.
- Match vocabulary to education level: {education_level}
- Do not use technical jargon for blue-collar or informal workers.
- Questions must sound like a real person asking, not a form field.
- Do not number the questions or add any preamble or explanation.

Topics already covered in this conversation: {covered_topics}

Return ONLY this JSON structure:
{{
  "questions": [
    {{
      "question": "question text",
      "question_type": "mcq",
      "options": ["chip1", "chip2", "chip3", ...],
      "allows_multiple": true|false,
      "allows_other": true,
      "skill_probing": "skill/topic name"
    }},
    ...
  ],
  "phase": {phase_number},
  "phase_name": "{phase_name}"
}}
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
  topics covered in previous batches.
  """
  topics = []
  for msg in conversation_history:
    if msg.get("role") == "assistant":
      try:
        content = msg.get("content", "")
        if not content:
          continue
        obj = json.loads(content)
        if isinstance(obj, dict) and obj.get("questions"):
          for q in obj["questions"]:
            if q.get("skill_probing"):
              topics.append(str(q["skill_probing"]))
      except (json.JSONDecodeError, TypeError, KeyError):
        pass
  return ", ".join(topics) if topics else "none yet"

def format_qa_pairs(conversation_history: list) -> str:
  """
  Formats conversation history into readable Q&A text for
  the skill extraction prompt. Handles batches.
  """
  pairs = []
  last_questions = []
  for msg in conversation_history:
    if msg.get("role") == "assistant":
      try:
        obj = json.loads(msg["content"])
        last_questions = [q["question"] for q in obj.get("questions", [])]
      except (json.JSONDecodeError, KeyError):
        last_questions = [msg["content"]]
    elif msg.get("role") == "user" and last_questions:
      try:
        # Answers come in two formats:
        # 1. Dict (new): {"0": ["Python", "SQL"], "1": "3", ...}  — keys are question indices
        # 2. List (legacy): ["answer1", "answer2", ...]
        answers_raw = json.loads(msg["content"])
        if isinstance(answers_raw, dict):
          # New format: iterate by sorted index key
          for idx_str in sorted(answers_raw.keys(), key=lambda k: int(k)):
            idx = int(idx_str)
            q = last_questions[idx] if idx < len(last_questions) else f"Question {idx + 1}"
            a = answers_raw[idx_str]
            a_str = ", ".join(a) if isinstance(a, list) else str(a)
            pairs.append(f"Q: {q}\nA: {a_str}")
        elif isinstance(answers_raw, list):
          for q, a in zip(last_questions, answers_raw):
            a_str = ", ".join(a) if isinstance(a, list) else str(a)
            pairs.append(f"Q: {q}\nA: {a_str}")
        else:
          pairs.append(f"Q: {last_questions[0]}\nA: {answers_raw}")
      except (json.JSONDecodeError, TypeError):
        pairs.append(f"Q: {last_questions[0]}\nA: {msg['content']}")
      last_questions = []
  return "\n\n".join(pairs) if pairs else "No answers recorded."

# ── Core Functions ────────────────────────────────────────────────

async def generate_next_question(
  session: dict,
  user_profile: dict,
  llm_provider
) -> dict:
  """
  Generates the next batch of adaptive questions using LLM.
  """
  current_q_count = session.get("current_question_number", 0)
  phase_num = get_phase_for_question(current_q_count + 1)
  phase = get_phase_config(phase_num)

  # Calculate batch size based on phase remaining questions
  max_phase_q = phase.get("max_questions", 4)
  remaining_in_phase = max_phase_q - (current_q_count % max_phase_q) 
  batch_size = min(3, remaining_in_phase) if remaining_in_phase > 0 else 3

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
    phase_number=phase_num,
    batch_size=batch_size
  )

  messages = [{"role": "system", "content": system_content}]
  messages.extend(conversation_history)

  logger.info(
    f"[ASSESSMENT] Generating batch of {batch_size} questions for "
    f"user={user_profile.get('user_id')}. Phase={phase['name']}."
  )

  from app.core.llm_config import LLM_TASKS
  from app.schemas.internal.llm_outputs import AssessmentBatchLLMOutput
  batch_raw = await llm_provider.complete_json(
    messages=messages,
    config=LLM_TASKS["assessment"]
  )

  try:
    if not batch_raw:
        raise ValueError("Empty response from LLM")
    
    batch_model = AssessmentBatchLLMOutput.model_validate(batch_raw)
    batch_obj = batch_model.model_dump()
    
  except Exception as e:
    logger.error(f"[ASSESSMENT] Failed to validate batch JSON: {e}")
    # Fallback healing logic
    batch_obj = batch_raw if batch_raw else {"questions": []}
    
    if "phase" not in batch_obj:
      batch_obj["phase"] = phase_num
    if "phase_name" not in batch_obj:
      batch_obj["phase_name"] = phase["name"]
    if not batch_obj.get("questions"):
      batch_obj["questions"] = [{
        "question": "Can you tell me more about your daily tasks?",
        "question_type": "mcq",
        "options": ["Very manual", "Mostly technical", "Supervisory"],
        "allows_multiple": False,
        "allows_other": True,
        "skill_probing": "general tasks"
      }]

  logger.info(
    f"[ASSESSMENT] Batch of {len(batch_obj['questions'])} generated."
  )

  return batch_obj


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
