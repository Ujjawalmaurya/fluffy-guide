import json
from loguru import logger
from fastapi import HTTPException
from app.modules.ai_chat.providers.base import IStructuredProvider
from app.core.llm_config import RESUME_PARSE
from models.resume_analysis_models import StructuredProfile, Skill
from services.pdf_extractor import extract_resume_text

# [RESUME_ANALYSIS] System prompt for deep extraction
RESUME_EXTRACTION_PROMPT = """
You are an expert resume parser and career advisor. Your task is to extract a highly structured profile from the provided resume text.
You must return ONLY valid JSON that matches the following structure:

{
  "full_name": "string",
  "contact_email": "string",
  "contact_phone": "string",
  "skills": [{"name": "string", "level": "beginner|intermediate|advanced"}],
  "soft_skills_inferred": ["string"],
  "experiences": [
    {
      "company": "string",
      "role": "string",
      "duration_months": number,
      "responsibilities": ["string"],
      "achievements": ["string"]
    }
  ],
  "education": [{"degree": "string", "institution": "string", "year": number}],
  "career_trajectory": {"direction": "ascending|lateral|descending|unclear", "summary": "string"},
  "has_photo_mentioned": boolean,
  "has_caste_religion_info": boolean,
  "interests": ["string"]
}

Follow these strict rules:
1. Extract ALL fields defined above.
2. For each experience entry:
   - Separate achievements (points that include numbers, metrics, percentages, or specific outcomes) 
   - From responsibilities (points that describe duties without specific quantified results).
3. Infer skill levels (beginner, intermediate, advanced) based on context.
4. Detect soft skills from the language used: e.g., "led team" -> Leadership.
5. If a field is missing, use null or an empty list/dict as appropriate.
6. Extract professional or career interests or key fields of interest (interests) from the resume text (e.g. software engineering, digital marketing, finance, agriculture).

Output must be ONLY the JSON object. No markdown, no preamble.
"""

def normalize_ai_output(data: dict) -> dict:
    """
    Cleans up common AI output variations to ensure Pydantic validation passes.
    """
    # 0. Handle top-level field synonyms
    if "name" in data and "full_name" not in data:
        data["full_name"] = data["name"]
    
    if "experience" in data and "experiences" not in data:
        data["experiences"] = data["experience"]

    if "interests" not in data:
        data["interests"] = []
    elif isinstance(data["interests"], str):
        data["interests"] = [data["interests"]]
    elif not isinstance(data["interests"], list):
        data["interests"] = []

    # 1. Handle "skills" - must be list of Skill objects
    if isinstance(data.get("skills"), list):
        normalized_skills = []
        for s in data["skills"]:
            if isinstance(s, dict):
                # Handle synonyms: skill_name, skill, name
                name = s.get("name") or s.get("skill") or s.get("skill_name") or "Unknown Skill"
                # Handle synonyms: level, proficiency, proficiency_level
                level = s.get("level") or s.get("proficiency") or s.get("proficiency_level")
                if isinstance(level, str):
                    level = level.lower()
                
                normalized_skills.append({
                    "name": str(name),
                    "level": level if level in ["beginner", "intermediate", "advanced"] else "intermediate"
                })
            elif isinstance(s, str):
                normalized_skills.append({"name": s, "level": "intermediate"})
        data["skills"] = normalized_skills
    elif isinstance(data.get("skills"), dict):
        # AI nested skills inside a key
        normalized_skills = []
        for key, val in data["skills"].items():
            if isinstance(val, list):
                for item in val:
                    if isinstance(item, str):
                        normalized_skills.append({"name": item, "level": "intermediate"})
                    elif isinstance(item, dict):
                        name = item.get("name") or item.get("skill") or item.get("skill_name") or str(item)
                        normalized_skills.append({"name": name, "level": "intermediate"})
        data["skills"] = normalized_skills
    else:
        data["skills"] = []

    # 2. Handle "experiences" inner field synonyms and nulls
    if isinstance(data.get("experiences"), list):
        normalized_exp = []
        for exp in data["experiences"]:
            if isinstance(exp, dict):
                # Handle duration vs duration_months
                if "duration" in exp and "duration_months" not in exp:
                    dur = exp["duration"]
                    if isinstance(dur, int):
                        exp["duration_months"] = dur
                    elif isinstance(dur, dict):
                        # start_year/end_year to months (rough)
                        start = dur.get("start_year")
                        end = dur.get("end_year") or dur.get("start_year")
                        if start and end:
                            exp["duration_months"] = (int(end) - int(start) + 1) * 12

                # Enforce defaults/null handling for ExperienceEntry to prevent Pydantic ValidationErrors
                exp["company"] = exp.get("company") or "Unknown Company"
                exp["role"] = exp.get("role") or "Role not specified"
                
                dur_m = exp.get("duration_months")
                if dur_m is None or not isinstance(dur_m, (int, float)):
                    exp["duration_months"] = 0
                else:
                    exp["duration_months"] = int(dur_m)
                
                sen = exp.get("seniority_level")
                if sen not in ["junior", "mid", "senior", "lead", "unclear"]:
                    exp["seniority_level"] = "unclear"
                
                for list_f in ["skills_used", "achievements", "responsibilities"]:
                    if not isinstance(exp.get(list_f), list):
                        exp[list_f] = []
                        
                ach_ratio = exp.get("achievement_ratio")
                if ach_ratio is None or not isinstance(ach_ratio, (int, float)):
                    exp["achievement_ratio"] = 0.0
                else:
                    exp["achievement_ratio"] = float(ach_ratio)
                
                normalized_exp.append(exp)
        data["experiences"] = normalized_exp
    else:
        data["experiences"] = []

    # 2b. Handle "education" nulls
    if isinstance(data.get("education"), list):
        normalized_edu = []
        for edu in data["education"]:
            if isinstance(edu, dict):
                edu["degree"] = edu.get("degree") or "Degree not specified"
                edu["institution"] = edu.get("institution") or "Institution not specified"
                
                if edu.get("is_vocational") is None:
                    edu["is_vocational"] = False
                if edu.get("is_certified") is None:
                    edu["is_certified"] = False
                
                normalized_edu.append(edu)
        data["education"] = normalized_edu
    else:
        data["education"] = []

    # 3. Handle "career_trajectory"
    ct = data.get("career_trajectory")
    if isinstance(ct, str):
        data["career_trajectory"] = {
            "direction": "unclear",
            "summary": ct
        }
    elif ct is None:
         data["career_trajectory"] = {
            "direction": "unclear",
            "summary": "No trajectory detected"
        }
    
    # 4. Ensure essential lists exist with safe defaults
    list_fields = [
        "experiences", "education", "languages_known", 
        "certifications", "soft_skills_inferred", "skills"
    ]
    for field in list_fields:
        if not isinstance(data.get(field), list):
            data[field] = []

    # 5. Enforce defaults for boolean flags
    for bool_field in ["has_photo_mentioned", "has_caste_religion_info", "has_linkedin", "has_github", "has_summary_section"]:
        if data.get(bool_field) is None:
            data[bool_field] = False

    return data

async def extract_structured_profile(raw_text: str, llm_provider: IStructuredProvider) -> StructuredProfile:
    """
    Takes raw resume text and returns a StructuredProfile using local Ollama.
    """
    messages = [
        {"role": "system", "content": RESUME_EXTRACTION_PROMPT},
        {"role": "user", "content": f"Resume Text:\n{raw_text}"}
    ]
    
    logger.info("[RESUME_ANALYSIS] starting Ollama extraction...")
    
    try:
        # Use complete_json for robust extraction with Ollama, passing schema
        data = await llm_provider.complete_json(prompt=messages, schema=StructuredProfile, config=RESUME_PARSE)
        
        # Normalize and Validate
        clean_data = normalize_ai_output(data)
        profile = StructuredProfile(**clean_data)
        
        logger.info(f"[RESUME_ANALYSIS] extraction_complete skills_count={len(profile.skills)}")
        return profile
        
    except Exception as e:
        logger.error(f"[RESUME_ANALYSIS] extraction_failed: {str(e)}")
        # Partial recovery: return empty profile instead of crashing
        return StructuredProfile()
