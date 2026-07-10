import json
from app.modules.ai_chat.providers.base import IStructuredProvider
from app.modules.assessment.phase_config import (
  get_phase_for_question, get_phase_config, PHASE_QUESTION_RANGES
)
from app.core.logger import get_logger
from app.core.llm_config import LLM_TASKS, CONCISENESS_INSTRUCTION
from app.core.config import settings
from app.schemas.internal.llm_outputs import AssessmentBatchLLMOutput, SkillExtractionLLMOutput

logger = get_logger("ASSESSMENT")

# ── Prompt Templates ─────────────────────────────────────────────

QUESTION_SYSTEM_PROMPT = """ROLE: You are SkillBridge AI, a sharp, empathetic career mentor.
Speaking with a {user_type} from {state}, education: {education_level}.
{background_context}

TASK: Generate EXACTLY {batch_size} distinct assessment questions to map their skill depth.

STYLE: Punchy, high-agency, ZERO corporate fluff. Match vocabulary to {education_level}.

CONTEXT:
- Phase: {phase_name}
- Goal: {phase_goal}
- Instruction: {phase_instruction}
- Probed Topics: {covered_topics}

JSON STRUCTURE:
{{
  "questions": [
    {{
      "question": "...",
      "question_type": "mcq",
      "options": ["...", "..."],
      "allows_multiple": true|false,
      "allows_other": true,
      "skill_probing": "..."
    }}
  ],
  "phase": {phase_number},
  "phase_name": "{phase_name}"
}}

RULES:
- Maximum 15 words per question.
- 3-8 short chips. Use "Other" (allows_other: true) for free-form depth.
- Use {language} language.
- Never repeat a topic from 'Probed Topics'.
- **NO PARROTING**: Do not use the user's previous answers as the choices/options in subsequent questions. Options should provide new alternatives, tools, or concepts to select from.
- **DIFFICULTY**: If they answer confidently, push deeper. If they struggle, simplify.
- **VARIETY**: Mix MCQ with single-choice. Avoid predictable patterns.
- Be creative. Don't sound like a bureaucrat.

{CONCISENESS_INSTRUCTION}
"""

SKILL_EXTRACTION_SYSTEM_PROMPT = """ROLE: You are an elite career analyst for SkillBridge AI.
TASK: Extract skills and insights from assessment responses.
JSON ONLY. No prose. No markdown. No explanation.

USER PROFILE:
- Type: {user_type}
- State: {state}
- Education: {education_level}
{background_context}

JSON STRUCTURE:
{{
  "skills": [
    {{
      "skill_name": "...",
      "category": "technical|soft|domain|tool|language",
      "proficiency_numeric": 1-5,
      "proficiency_label": "Beginner|Elementary|Intermediate|Advanced|Expert",
      "confidence": 0.0-1.0,
      "evidence": "exact phrase from answers"
    }}
  ],
  "career_goals": ["..."],
  "blockers": ["..."],
  "work_preferences": {{
    "environment": "team|solo|mixed",
    "timing": "fixed|flexible",
    "location_flexible": true|false
  }},
  "assessment_summary": "2 sentence specific summary"
}}

RULES:
- Only include explicitly demonstrated skills.
- Evidence must be real phrases.
- Summary must be warm and specific.

{CONCISENESS_INSTRUCTION}
"""

# ── Helper Functions ─────────────────────────────────────────────

def extract_covered_topics(conversation_history: list) -> str:
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
            probing = q.get("skill_probing")
            if probing:
              # Ensure it's a string
              topics.append(str(probing))
      except (json.JSONDecodeError, TypeError, KeyError):
        pass
  return ", ".join(topics) if topics else "none yet"

def _format_answer(a: any) -> str:
  """Safely formats an answer, extracting label/value from dicts if needed."""
  if isinstance(a, list):
    return ", ".join(_format_answer(item) for item in a)
  if isinstance(a, dict):
    # Handle chip-like objects: {"label": "...", "value": "..."}
    return str(a.get("label") or a.get("value") or a)
  return str(a)

def format_qa_pairs(conversation_history: list) -> str:
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
        answers_raw = json.loads(msg["content"])
        if isinstance(answers_raw, dict):
          for idx_str in sorted(answers_raw.keys(), key=lambda k: int(k)):
            idx = int(idx_str)
            q = last_questions[idx] if idx < len(last_questions) else f"Question {idx + 1}"
            a = answers_raw[idx_str]
            pairs.append(f"Q: {q}\nA: {_format_answer(a)}")
        elif isinstance(answers_raw, list):
          for q, a in zip(last_questions, answers_raw):
            pairs.append(f"Q: {q}\nA: {_format_answer(a)}")
        else:
          pairs.append(f"Q: {last_questions[0]}\nA: {_format_answer(answers_raw)}")
      except (json.JSONDecodeError, TypeError):
        pairs.append(f"Q: {last_questions[0]}\nA: {msg['content']}")
      last_questions = []
  return "\n\n".join(pairs) if pairs else "No answers recorded."


def _get_background_context(user_profile: dict) -> str:
  """Builds a clean background context string from profile data to supply to prompt."""
  parts = []
  
  # Role / Trade
  role = user_profile.get("primary_role") or user_profile.get("primary_trade") or user_profile.get("current_work_type")
  if role:
    parts.append(f"- Role/Trade of Interest: {role}")
    
  # Resume skills / interests
  resume_skills = user_profile.get("resume_skills")
  if resume_skills:
    skills_str = ", ".join(resume_skills) if isinstance(resume_skills, list) else str(resume_skills)
    parts.append(f"- Known Skills: {skills_str}")
    
  # General career interests
  interests = user_profile.get("career_interests") or user_profile.get("target_roles") or user_profile.get("interests")
  if interests:
    interests_str = ", ".join(interests) if isinstance(interests, list) else str(interests)
    parts.append(f"- Career Interests: {interests_str}")
    
  if not parts:
    return ""
    
  return "\nBACKGROUND CONTEXT:\n" + "\n".join(parts)


# ── Core Functions ────────────────────────────────────────────────

async def generate_next_question(
  session: dict,
  user_profile: dict,
  llm_provider: IStructuredProvider
) -> dict:
  """Generates the next batch of adaptive questions using LLM."""
  current_q_count = session.get("current_question_number", 0)
  phase_num = get_phase_for_question(current_q_count + 1)
  phase = get_phase_config(phase_num)

  # Correctly calculate remaining in current phase using defined ranges
  phase_range = PHASE_QUESTION_RANGES.get(phase_num, (1, 11))
  phase_end = phase_range[1]
  remaining_in_phase = phase_end - current_q_count
  
  # Also respect the global limit
  remaining_total = settings.assessment_max_questions - current_q_count
  
  batch_size = min(3, remaining_in_phase, remaining_total)
  batch_size = max(1, batch_size) 

  conversation_history = session.get("adaptive_context", [])
  covered_topics = extract_covered_topics(conversation_history)
  qa_context = format_qa_pairs(conversation_history)

  system_content = QUESTION_SYSTEM_PROMPT.format(
    user_type=user_profile.get("user_type", "individual"),
    state=user_profile.get("state", "India"),
    education_level=user_profile.get("education_level", "not specified"),
    phase_name=phase["name"],
    phase_goal=phase["goal"],
    phase_instruction=phase["instruction"],
    language="Hindi" if user_profile.get("preferred_lang") == "hi" else "English",
    covered_topics=covered_topics,
    phase_number=phase_num,
    batch_size=batch_size,
    background_context=_get_background_context(user_profile),
    CONCISENESS_INSTRUCTION=CONCISENESS_INSTRUCTION
  )

  if qa_context and qa_context != "No answers recorded.":
    system_content += f"\n\nPREVIOUS Q&A (Do NOT repeat these topics):\n{qa_context}"

  messages = [{"role": "system", "content": system_content}]
  messages.extend(conversation_history)

  logger.info(f"[ASSESSMENT] Generating batch for user={user_profile.get('user_id')}. Phase={phase['name']}.")

  batch_raw = await llm_provider.complete_json(
    messages=messages,
    config=LLM_TASKS["assessment"]
  )

  try:
    if not batch_raw: raise ValueError("Empty response from LLM")
    batch_obj = AssessmentBatchLLMOutput.model_validate(batch_raw).model_dump()
  except Exception as e:
    logger.error(f"[ASSESSMENT] Validation failed: {e}")
    batch_obj = batch_raw if batch_raw else {"questions": []}
    if "phase" not in batch_obj: batch_obj["phase"] = phase_num
    if "phase_name" not in batch_obj: batch_obj["phase_name"] = phase["name"]
    if not batch_obj.get("questions"):
      batch_obj["questions"] = [{
        "question": "Can you tell me more about your daily tasks?",
        "question_type": "mcq",
        "options": ["Very manual", "Mostly technical", "Supervisory"],
        "allows_multiple": False, "allows_other": True, "skill_probing": "general tasks"
      }]
  return batch_obj

async def extract_skills_from_session(
  session: dict,
  user_profile: dict,
  llm_provider: IStructuredProvider
) -> dict:
  """Uses LLM for skill extraction from completed assessment."""
  conversation_history = session.get("adaptive_context", [])
  qa_pairs = format_qa_pairs(conversation_history)

  system_prompt = SKILL_EXTRACTION_SYSTEM_PROMPT.format(
    user_type=user_profile.get("user_type", "individual"),
    state=user_profile.get("state", "India"),
    education_level=user_profile.get("education_level", "not specified"),
    background_context=_get_background_context(user_profile),
    CONCISENESS_INSTRUCTION=CONCISENESS_INSTRUCTION
  )

  user_prompt = f"ASSESSMENT QA PAIRS:\n{qa_pairs}\n\nExtract insights now."

  logger.info(f"[ASSESSMENT] Extracting skills for user={user_profile.get('user_id')}.")

  extracted_raw = await llm_provider.complete_json(
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ],
    config=LLM_TASKS["assessment_extraction"]
  )

  try:
    if not extracted_raw: raise ValueError("Empty response from LLM")
    extracted = SkillExtractionLLMOutput.model_validate(extracted_raw).model_dump()
  except Exception as e:
    logger.error(f"[ASSESSMENT] Skill extraction validation failed: {e}")
    extracted = SkillExtractionLLMOutput().model_dump()

  return extracted
