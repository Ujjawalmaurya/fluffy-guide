# [RESUME_PARSER] Extracts structured career data from resume PDF.
# Uses robust multi-stage extraction (PyMuPDF + OCR fallback), Ollama for intelligence.
# Returns structured JSON — aligned with Pydantic for reliability.

import io
import json
from typing import List, Optional
from loguru import logger
from pydantic import BaseModel, Field

from app.modules.ai_chat.providers.ollama_provider import OllamaProvider
from app.shared.exceptions import ResumeNoText, AppError
from services.pdf_extractor import extract_resume_text
from app.core import llm_config

# --- Pydantic Schemas for Strict Parsing ---

class PersonalInfo(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None

class Education(BaseModel):
    degree: str
    institution: str
    year_range: Optional[str] = None
    level: str = Field(description="undergraduate | postgraduate | diploma | phd")
    coursework: Optional[List[str]] = None

class Experience(BaseModel):
    title: str
    company: str
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: bool = False
    responsibilities: List[str]
    technologies: List[str]

class Skill(BaseModel):
    name: str
    category: str = Field(description="technical | soft | tool")
    proficiency: str = Field(description="Beginner | Intermediate | Advanced | Expert")

class ResumeData(BaseModel):
    personal_info: PersonalInfo
    primary_role: str
    total_experience_years: int
    education: List[Education]
    experience: List[Experience]
    skills: List[Skill]
    summary: str
    strengths: List[str]
    weaknesses: List[str]
    career_suggestions: List[str]
    skill_gap_analysis: str

# Optimized prompt following HARD RULES
RESUME_EXTRACTION_PROMPT = """Extract career data from resume. JSON ONLY.
Schema:
- personal_info: {name, email, phone, location, linkedin}
- primary_role: job title (max 3 words)
- total_experience_years: int
- education: [{degree, institution, year_range, level, coursework}]
- experience: [{title, company, location, start_date, end_date, is_current, responsibilities, technologies}]
- skills: [{name, category, proficiency}]
- summary: professional summary (max 20 words)
- strengths: [string] (max 3)
- weaknesses: [string] (max 3)
- career_suggestions: [string] (max 3)
- skill_gap_analysis: missing skill (max 10 words)

Resume:
{resume_text}"""


async def parse_resume(file_bytes: bytes, filename: str, content_type: str, user_id: str,
                       llm_provider: OllamaProvider) -> dict:
    
    logger.info(f"[RESUME_PARSER] Processing user={user_id} file={filename}")
    text = ""
    
    try:
        if filename.lower().endswith(".pdf"):
            text = extract_resume_text(file_bytes)
        elif filename.lower().endswith(".docx"):
            import docx
            doc = docx.Document(io.BytesIO(file_bytes))
            text = "\n".join([para.text for para in doc.paragraphs])
        else:
            text = file_bytes.decode("utf-8", errors="ignore")
    except Exception as e:
        logger.error(f"[RESUME_PARSER] File extraction failed: {str(e)}")
        raise ResumeNoText()
                
    if len(text.strip()) < 50:
        logger.warning(f"[RESUME_PARSER] Minimal text found for user={user_id}")
        raise ResumeNoText()
        
    # Token optimization: 3000 chars is ~750 tokens, perfect for fast inference
    if len(text) > 3000:
        text = text[:3000]
        
    formatted_prompt = RESUME_EXTRACTION_PROMPT.format(resume_text=text)
    
    try:
        logger.info(f"[RESUME_PARSER] Prompting LLM for extraction...")
        parsed_dict = await llm_provider.complete_json(
            messages=[{"role": "user", "content": formatted_prompt}],
            config=llm_config.RESUME_PARSE
        )
        
        # Pydantic validation 
        try:
            # 1. HEALING: Fix common structural issues BEFORE validation
            if isinstance(parsed_dict.get("total_experience_years"), str):
                try:
                    import re
                    # Extract first number from string like "5 years"
                    num_match = re.search(r"\d+", parsed_dict["total_experience_years"])
                    parsed_dict["total_experience_years"] = int(num_match.group(0)) if num_match else 0
                except:
                    parsed_dict["total_experience_years"] = 0
            
            # Ensure primary_role is a string
            if not parsed_dict.get("primary_role"):
                parsed_dict["primary_role"] = "Professional"

            # Fix Education: Ensure 'level' is present and valid
            if isinstance(parsed_dict.get("education"), list):
                valid_levels = ["undergraduate", "postgraduate", "diploma", "phd"]
                for edu in parsed_dict["education"]:
                    if not edu.get("level") or str(edu.get("level")).lower() not in valid_levels:
                        edu["level"] = "undergraduate" # Default fallback

            # Fix Experience: Ensure lists exist
            if isinstance(parsed_dict.get("experience"), list):
                for exp in parsed_dict["experience"]:
                    if not isinstance(exp.get("responsibilities"), list): exp["responsibilities"] = []
                    if not isinstance(exp.get("technologies"), list): exp["technologies"] = []

            # Fix Skills: Ensure category and proficiency
            if isinstance(parsed_dict.get("skills"), list):
                for sk in parsed_dict["skills"]:
                    if not sk.get("category"): sk["category"] = "technical"
                    if not sk.get("proficiency"): sk["proficiency"] = "Intermediate"

            # Ensure summary and analysis
            if not parsed_dict.get("summary"): parsed_dict["summary"] = "Experienced professional."
            if not parsed_dict.get("skill_gap_analysis"): parsed_dict["skill_gap_analysis"] = "Continuous learning recommended."

            # Ensure arrays are actual arrays
            for list_field in ["education", "experience", "skills", "strengths", "weaknesses", "career_suggestions"]:
                if list_field in parsed_dict and not isinstance(parsed_dict[list_field], list):
                    parsed_dict[list_field] = []

            validated_data = ResumeData(**parsed_dict)
            final_dict = validated_data.model_dump()
        except Exception as ve:
            logger.warning(f"[RESUME_PARSER] Validation failed: {str(ve)}. Using healed dict.")
            # If Pydantic still fails, we use the dict as-is (best effort)
            final_dict = parsed_dict
            # Final safety net for critical fields
            if "skills" not in final_dict: final_dict["skills"] = []
            if "primary_role" not in final_dict: final_dict["primary_role"] = "Professional"

    except AppError as e:
        logger.error(f"[RESUME_PARSER] AI Extraction failed: {e.message}")
        raise
    except Exception as e:
        logger.error(f"[RESUME_PARSER] Unexpected parsing failure: {str(e)}")
        # Log the raw text to see if it was too messy
        logger.debug(f"[RESUME_PARSER] Resume text snippet: {text[:500]}...")
        raise AppError("LLM_PARSE_ERROR", f"Could not parse resume data. Error: {str(e)}")
        
    logger.info(f"[RESUME_PARSER] Success for user={user_id}. Skills={len(final_dict.get('skills', []))}")
    
    return {
        "parsed": final_dict,
        "raw_text": text
    }
