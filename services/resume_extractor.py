import json
from loguru import logger
from fastapi import HTTPException
from app.modules.ai_chat.providers.gemini import get_gemini_instance
from models.resume_analysis_models import StructuredProfile, Skill
from services.pdf_extractor import extract_resume_text

# [RESUME_ANALYSIS] System prompt for deep extraction
RESUME_EXTRACTION_PROMPT = """
You are an expert resume parser and career advisor. Your task is to extract a highly structured profile from the provided resume text.
You must return ONLY valid JSON that matches the specified schema.

Follow these strict rules:
1. Extract ALL fields defined in the schema.
2. For each experience entry:
   - Separate achievements (points that include numbers, metrics, percentages, or specific outcomes) 
   - From responsibilities (points that describe duties without specific quantified results).
3. Infer skill levels (beginner, intermediate, advanced) based on:
   - Years of usage mentioned.
   - Seniority of the roles where the skill was used.
   - Complexity of projects described.
4. Detect soft skills from the language used: e.g., "led team" -> Leadership, "coordinated" -> Coordination, "client-facing" -> Client Management.
5. Infer career trajectory (ascending, lateral, descending, unclear) based on the sequence and growth in roles.
6. Flag India-specific resume issues:
   - Presence of a photo.
   - Mention of caste, religion, or community.
   - Excessive length of the references section.
   - Father's name or other overly personal details common in some Indian CVs.
7. Detect vocational qualifications and certificates: ITI, Polytechnic, Diploma, NSDC, PMKVY, etc.
8. Infer potential target roles: Based on the candidate's skills and experience, list 3-5 specific job titles they are well-qualified for (e.g., "Full Stack Developer", "Cloud Architect").
9. If a field is missing, use null or an empty list/dict as appropriate.

Output must be ONLY the JSON object. No markdown, no preamble.
"""

def normalize_ai_output(data: dict) -> dict:
    """
    Cleans up common AI output variations to ensure Pydantic validation passes.
    """
    # 0. Handle "inferred_target_roles"
    if not isinstance(data.get("inferred_target_roles"), list):
        data["inferred_target_roles"] = []
    
    # 1. Handle "skills" - must be list of Skill objects
    if isinstance(data.get("skills"), list):
        normalized_skills = []
        for s in data["skills"]:
            if isinstance(s, dict):
                # Handle {"skill": "..."} vs {"name": "..."}
                name = s.get("name") or s.get("skill") or "Unknown Skill"
                level = s.get("level")
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
                        name = item.get("name") or item.get("skill") or str(item)
                        normalized_skills.append({"name": name, "level": "intermediate"})
        data["skills"] = normalized_skills
    else:
        data["skills"] = []

    # 2. Handle "career_trajectory"
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
    
    # 3. Ensure essential lists exist with safe defaults
    list_fields = [
        "experiences", "education", "languages_known", 
        "certifications", "soft_skills_inferred", "skills"
    ]
    for field in list_fields:
        if not isinstance(data.get(field), list):
            data[field] = []

    # 4. Enforce defaults for boolean flags
    for bool_field in ["has_photo_mentioned", "has_caste_religion_info", "has_linkedin", "has_github", "has_summary_section"]:
        if data.get(bool_field) is None:
            data[bool_field] = False

    return data

async def extract_structured_profile(raw_text: str) -> StructuredProfile:
    """
    Takes raw resume text and returns a StructuredProfile using Gemini 1.5 Flash.
    """
    gemini = get_gemini_instance()
    
    messages = [
        {"role": "system", "content": RESUME_EXTRACTION_PROMPT},
        {"role": "user", "content": f"Resume Text:\n{raw_text}"}
    ]
    
    logger.info("[RESUME_ANALYSIS] starting Gemini extraction...")
    
    try:
        # Use the specialized lite model for resume depth analysis as requested
        response_text = await gemini.complete(messages, model_name="gemini-2.0-flash-lite-preview-02-05")
        
        # Strip potential markdown fences
        clean_json = response_text.strip()
        if clean_json.startswith("```json"):
            clean_json = clean_json[7:-3].strip()
        elif clean_json.startswith("```"):
            clean_json = clean_json[3:-3].strip()
            
        data = json.loads(clean_json)
        
        # Normalize and Validate
        clean_data = normalize_ai_output(data)
        profile = StructuredProfile(**clean_data)
        
        logger.info(f"[RESUME_ANALYSIS] extraction_complete skills_count={len(profile.skills)}")
        return profile
        
    except json.JSONDecodeError as e:
        logger.error(f"[RESUME_ANALYSIS] extraction_failed: JSON parse error. Response snippet: {response_text[:200]}")
        # Partial recovery: return empty profile if AI fails completely
        return StructuredProfile()
    except Exception as e:
        logger.error(f"[RESUME_ANALYSIS] extraction_failed: {str(e)}")
        # Partial recovery: return empty profile instead of crashing
        return StructuredProfile()
