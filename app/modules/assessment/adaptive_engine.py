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

# Here is how the questioning works:
# We feed the model user details, what topics we already probed, and the full chat history.
# The model must return a JSON response with exactly one question that adapts to the previous answer.
QUESTION_SYSTEM_PROMPT = """ROLE:
You are SkillBridge AI, a sharp, empathetic career counselor, industrial psychologist, and technical interviewer.
You are interviewing {full_name}, who is from the state of {state} and has an education level of: "{education_level}".
User Category: {user_type_desc}

OBJECTIVE:
Ask exactly {batch_size} targeted question to assess their actual skills, depth of knowledge, work style, motivators, and blockers.
Your goal is to gather high-quality, specific insights. Do not rush to recommend roles yet.
Each question should feel like a natural follow-up to their previous response.

STYLE:
Conversational, friendly, and direct. Zero corporate jargon.
Keep questions concise and easy to answer. Match your vocabulary to their education level.

CONTEXT:
- Assessment Phase: {phase_name}
- Phase Goal: {phase_goal}
- Specific Instruction for Phase: {phase_instruction}
- Already Probed Topics: {covered_topics}

JSON FORMAT REQUIRED:
{{
  "questions": [
    {{
      "question": "The actual question text here",
      "question_type": "text" | "mcq" | "rating",
      "options": ["Option A", "Option B"] or [],
      "allows_multiple": false,
      "allows_other": true,
      "skill_probing": "Name of the skill or topic being assessed"
    }}
  ],
  "phase": {phase_number},
  "phase_name": "{phase_name}"
}}

CRITICAL RULES:
1. Ask ONLY one question (batch_size is 1).
2. Adapt: read the previous answers in the history. If the user answered a question, push deeper on that skill or check for practical experience.
3. If they struggled or gave a brief answer, simplify the next question. If they answered confidently, probe their depth.
4. Avoid generic "What are your skills?" questions. Ask situational, behavioral, or trade-specific questions instead.
5. Use rating question type to let users self-assess (1 to 5) comfort levels with specific tools or tasks.
6. Use mcq type with options to let users pick chips, or text type for open-ended reflections.
7. Language: Speak in {language_choice}. Keep the phrasing natural and relatable.
8. Do not repeat topics listed in "Already Probed Topics".
9. Never reuse the user's exact words back as MCQ choices. Offer new alternatives or typical industry answers.
"""

# The extraction prompt builds the final report from the chat log.
# Since we bumped the token limit in llm_config, it can write a rich, detailed markdown summary.
SKILL_EXTRACTION_SYSTEM_PROMPT = """ROLE:
You are an expert career analyst, industrial psychologist, and senior vocational advisor.

TASK:
Analyze the complete Q&A assessment transcript of {full_name} and compile a highly structured, comprehensive career report.

USER DETAILS:
- Category: {user_type_desc}
- State: {state}
- Education: {education_level}
{background_context}

JSON FORMAT REQUIRED:
{{
  "skills": [
    {{
      "skill_name": "Name of skill",
      "category": "technical" | "soft" | "domain" | "tool" | "language",
      "proficiency_numeric": 1,
      "proficiency_label": "Beginner" | "Elementary" | "Intermediate" | "Advanced" | "Expert",
      "confidence": 0.8,
      "evidence": "Quote or paraphrase from their responses"
    }}
  ],
  "career_goals": ["Goal 1", "Goal 2"],
  "blockers": ["Blocker 1", "Blocker 2"],
  "work_preferences": {{
    "environment": "team" | "solo" | "mixed",
    "timing": "fixed" | "flexible",
    "location_flexible": true
  }},
  "assessment_summary": "Rich markdown summary"
}}

RULES FOR STRUCTURED SUMMARY:
The "assessment_summary" field must contain a beautiful, comprehensive Markdown document covering these sections:

# Executive Summary
[A summary of who they are, their strengths, work habits, and potential]

# Key Strengths
- **Primary Strengths**: [Strengths demonstrated with evidence]
- **Hidden Potentials**: [Talents inferred from hobbies, values, or background]

# Competency Profile
- **Technical & Practical Skills**: [Tools, machinery, software, or trades they know]
- **Soft Skills**: [Communication, teamwork, problem solving, organization]
- **Learning & Adaptability**: [How they learn, self-taught skills, adapt to change]

# Behavioral Profile
- **Work Style & Environment**: [Team vs solo, structure vs flexibility, risk attitude]
- **Motivators & Values**: [What drives them, company culture alignment, career values]

# Career Recommendation & Analytics
- **Readiness Score**: [Score 0-100 indicating job readiness with brief reasoning]
- **Confidence Index**: [Score 0-100 showing their self-belief based on the chat]
- **Top Recommended Careers**:
  1. [Career Name] ([Match %]%) - [Why they fit, active skills they have, and gap areas to fill]
  ... (List up to 5 highly relevant careers)

# Learning & Growth Action Plan
- **Skills to Build**: [Gaps they must bridge next]
- **Certifications & Training**: [Practical training or courses that would help]
- **Resume & Interview Advice**: [Practical tips for job hunting]
- **2-5 Year Outlook**: [Strategic plan for long-term career growth]

Ensure the summary is rich and comprehensive, bypassing standard conciseness constraints.
"""


# ── Helper Functions ─────────────────────────────────────────────

def _get_readable_user_type(user_type: str) -> str:
    # Maps internal user_type enums to clear descriptions for the LLM
    mapping = {
        "individual_youth": "Student / Youth seeking career opportunities",
        "individual_bluecollar": "Blue-collar worker / Skilled trade specialist",
        "individual_informal": "Informal sector worker / Daily wager / Freelancer"
    }
    return mapping.get(user_type, "Job Seeker")

def _get_readable_education(edu: str) -> str:
    # Map education code to clean readable text
    mapping = {
        "none": "No formal education",
        "primary": "Primary school",
        "secondary": "Secondary school (10th/12th grade)",
        "graduate": "College graduate",
        "postgrad": "Postgraduate degree"
    }
    return mapping.get(edu, edu or "Not specified")

def extract_covered_topics(conversation_history: list) -> str:
    # Extracts the probed skill topics from previous assistant messages
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
                            topics.append(str(probing))
            except (json.JSONDecodeError, TypeError, KeyError):
                pass
    return ", ".join(topics) if topics else "None yet"

def _format_answer(a: any) -> str:
    # Formats lists or dicts of answers to plain text strings
    if isinstance(a, list):
        return ", ".join(_format_answer(item) for item in a)
    if isinstance(a, dict):
        return str(a.get("label") or a.get("value") or a)
    return str(a)

def format_qa_pairs(conversation_history: list) -> str:
    # Groups questions and answers sequentially for LLM prompt context
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
    # Gathers background data like target roles or skills from resume
    parts = []
    
    role = user_profile.get("primary_role") or user_profile.get("primary_trade") or user_profile.get("current_work_type")
    if role:
        parts.append(f"- Role/Trade of Interest: {role}")
        
    resume_skills = user_profile.get("resume_skills")
    if resume_skills:
        skills_str = ", ".join(resume_skills) if isinstance(resume_skills, list) else str(resume_skills)
        parts.append(f"- Known Skills from Resume: {skills_str}")
        
    interests = user_profile.get("career_interests") or user_profile.get("target_roles") or user_profile.get("interests")
    if interests:
        interests_str = ", ".join(interests) if isinstance(interests, list) else str(interests)
        parts.append(f"- Declared Interests: {interests_str}")
        
    if not parts:
        return ""
        
    return "\nBACKGROUND CONTEXT:\n" + "\n".join(parts)

def _clean_conversation_history(conversation_history: list) -> list:
    # Converts assistant JSON nodes and user selection payloads into human-like chat lines
    cleaned = []
    for msg in conversation_history:
        role = msg.get("role")
        content = msg.get("content", "")
        if not content:
            continue
            
        if role == "assistant":
            try:
                obj = json.loads(content)
                questions = [q["question"] for q in obj.get("questions", [])]
                cleaned_content = " ".join(questions)
            except (json.JSONDecodeError, KeyError, TypeError):
                cleaned_content = content
            cleaned.append({"role": "assistant", "content": cleaned_content})
            
        elif role == "user":
            try:
                answers_raw = json.loads(content)
                if isinstance(answers_raw, dict):
                    answers = []
                    for idx_str in sorted(answers_raw.keys(), key=lambda k: int(k)):
                        answers.append(str(answers_raw[idx_str]))
                    cleaned_content = " ".join(answers)
                elif isinstance(answers_raw, list):
                    cleaned_content = " ".join(str(a) for a in answers_raw)
                else:
                    cleaned_content = str(answers_raw)
            except (json.JSONDecodeError, TypeError):
                cleaned_content = content
            cleaned.append({"role": "user", "content": cleaned_content})
        else:
            cleaned.append(msg)
            
    return cleaned


# ── Core Functions ────────────────────────────────────────────────

async def generate_next_question(
    session: dict,
    user_profile: dict,
    llm_provider: IStructuredProvider
) -> dict:
    # Calculate current step and corresponding phase config
    current_q_count = session.get("current_question_number", 0)
    phase_num = get_phase_for_question(current_q_count + 1)
    phase = get_phase_config(phase_num)

    # Force batch_size = 1 so assessment runs one conversational question at a time
    batch_size = 1

    conversation_history = session.get("adaptive_context", [])
    covered_topics = extract_covered_topics(conversation_history)
    qa_context = format_qa_pairs(conversation_history)

    # Map profile properties to friendly terms
    full_name = user_profile.get("full_name") or "User"
    user_type_desc = _get_readable_user_type(user_profile.get("user_type", ""))
    education_level = _get_readable_education(user_profile.get("education_level", ""))
    state = user_profile.get("state") or "India"
    
    # Check language preference (Hindi/English)
    preferred_lang = user_profile.get("preferred_lang")
    if preferred_lang == "hi":
        language_choice = "conversational Hindi (use Hindi words but write them in Devanagari script, keep questions simple and accessible)"
    else:
        language_choice = "clear, accessible English"

    system_content = QUESTION_SYSTEM_PROMPT.format(
        full_name=full_name,
        user_type_desc=user_type_desc,
        state=state,
        education_level=education_level,
        phase_name=phase["name"],
        phase_goal=phase["goal"],
        phase_instruction=phase["instruction"],
        language_choice=language_choice,
        covered_topics=covered_topics,
        phase_number=phase_num,
        batch_size=batch_size,
        background_context=_get_background_context(user_profile)
    )

    if qa_context and qa_context != "No answers recorded.":
        system_content += f"\n\nPREVIOUS QUESTIONS & ANSWERS IN THIS INTERVIEW:\n{qa_context}"

    messages = [{"role": "system", "content": system_content}]
    cleaned_history = _clean_conversation_history(conversation_history)
    messages.extend(cleaned_history)

    logger.info(f"[ASSESSMENT] Generating question {current_q_count + 1} (Phase {phase_num}) for user={full_name}.")

    batch_raw = await llm_provider.complete_json(
        messages=messages,
        config=LLM_TASKS["assessment"]
    )

    # Validate output structure or fallback gracefully
    try:
        if not batch_raw:
            raise ValueError("Empty response from local LLM")
            
        # Parse single question at root if LLM failed to wrap it in questions list
        if "question" in batch_raw and "questions" not in batch_raw:
            logger.warning("[ASSESSMENT] LLM returned single question at root. Wrapping in questions list.")
            batch_raw["questions"] = [{
                "question": batch_raw.pop("question"),
                "question_type": batch_raw.pop("question_type", "text"),
                "options": batch_raw.pop("options", []),
                "allows_multiple": batch_raw.pop("allows_multiple", False),
                "allows_other": batch_raw.pop("allows_other", True),
                "skill_probing": batch_raw.pop("skill_probing", "general")
            }]
            
        if "questions" in batch_raw and isinstance(batch_raw["questions"], dict):
            batch_raw["questions"] = [batch_raw["questions"]]
            
        batch_obj = AssessmentBatchLLMOutput.model_validate(batch_raw).model_dump()
    except Exception as e:
        logger.error(f"[ASSESSMENT] Validation failed: {e}")
        batch_obj = batch_raw if batch_raw else {"questions": []}
        if "phase" not in batch_obj:
            batch_obj["phase"] = phase_num
        if "phase_name" not in batch_obj:
            batch_obj["phase_name"] = phase["name"]
        if not batch_obj.get("questions"):
            # Provide a safe default question if AI failed completely
            batch_obj["questions"] = [{
                "question": "Can you describe a typical task you do in your daily routine?",
                "question_type": "text",
                "options": [],
                "allows_multiple": False,
                "allows_other": True,
                "skill_probing": "general routine"
            }]
            
    return batch_obj

async def extract_skills_from_session(
    session: dict,
    user_profile: dict,
    llm_provider: IStructuredProvider
) -> dict:
    conversation_history = session.get("adaptive_context", [])
    qa_pairs = format_qa_pairs(conversation_history)

    # Format descriptors for final extraction run
    full_name = user_profile.get("full_name") or "User"
    user_type_desc = _get_readable_user_type(user_profile.get("user_type", ""))
    education_level = _get_readable_education(user_profile.get("education_level", ""))
    state = user_profile.get("state") or "India"

    system_prompt = SKILL_EXTRACTION_SYSTEM_PROMPT.format(
        full_name=full_name,
        user_type_desc=user_type_desc,
        state=state,
        education_level=education_level,
        background_context=_get_background_context(user_profile)
    )

    user_prompt = f"ASSESSMENT QA PAIRS:\n{qa_pairs}\n\nPerform final extraction and write the report now."

    logger.info(f"[ASSESSMENT] Running final career report extraction for user={full_name}.")

    extracted_raw = await llm_provider.complete_json(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        config=LLM_TASKS["assessment_extraction"]
    )

    try:
        if not extracted_raw:
            raise ValueError("Empty response from extraction LLM")
        extracted = SkillExtractionLLMOutput.model_validate(extracted_raw).model_dump()
    except Exception as e:
        logger.error(f"[ASSESSMENT] Skill extraction validation failed: {e}")
        extracted = SkillExtractionLLMOutput().model_dump()

    return extracted
