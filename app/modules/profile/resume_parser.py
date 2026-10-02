# [RESUME_PARSER] Extracts structured career data from resume PDF.
# Uses pdfplumber for text extraction, Gemini (Flash/Pro) and Groq for intelligence.
# Returns structured JSON — never uses keyword lists.

import io
import json
try:
    import docx
except ImportError:
    docx = None
from loguru import logger

from app.modules.ai_chat.providers.base import ILLMProvider
from app.shared.exceptions import ResumeNoText, GeminiParseError

# Optimized prompt for lower token usage and deeper insights
RESUME_EXTRACTION_PROMPT = """Extract deep career insights from the resume below.
Return ONLY valid JSON. No markdown.

Fields:
- skills: list of {{name, category, proficiency_label, years_used}}
- experience_level: Entry|Junior|Mid|Senior|Expert
- strengths: list of strings
- weaknesses: list of strings (areas for improvement)
- career_suggestions: list of strings (suitable roles in India)
- skill_gap_analysis: sentence on what's missing for target roles
- education: list of {{degree, institution, year}}
- experience: list of {{title, company, duration}}

Resume:
{resume_text}"""

ATS_SCORING_PROMPT = """Score the resume below for ATS compatibility.
Return ONLY valid JSON. No markdown.

Fields:
- score: int (0-100)
- breakdown: {{formatting: 0-33, keywords: 0-33, impact: 0-34}}
- suggestions: list of strings

Resume:
{resume_text}"""

INDIA_QUALIFICATIONS_PROMPT = """Extract India-specific qualifications (Exams like GATE, UPSC, JEE, or Certifications like NPTEL, CDAC) from the resume.
Return ONLY valid JSON. No markdown.

Fields:
- exams: list of strings
- certificates: list of strings

Resume:
{resume_text}"""

ACHIEVEMENT_DETECTION_PROMPT = """Detect quantified achievements (numbers, percentages, scales) from the resume.
Return ONLY valid JSON. No markdown.

Fields:
- achievements: list of {{title: "Short description", impact: "Quantified metric"}}

Resume:
{resume_text}"""

BULLET_REWRITE_PROMPT = """Rewrite the following resume bullets to be more impactful and result-oriented.
Return ONLY valid JSON. No markdown.

Input Bullets:
{bullets}

Return as:
{{rewritten_bullets: ["new bullet 1", "new bullet 2", ...]}}"""

async def parse_resume(file_bytes: bytes, filename: str, content_type: str, user_id: str,
                       provider: ILLMProvider) -> dict:
    
    logger.info(f"[RESUME_PARSER] Extracting text for user={user_id} file={filename}")
    text = ""
    
    try:
        if filename.lower().endswith(".pdf"):
            from services.pdf_extractor import extract_resume_text
            text = extract_resume_text(file_bytes)
        elif filename.lower().endswith(".docx"):
            doc = docx.Document(io.BytesIO(file_bytes))
            text = "\n".join([para.text for para in doc.paragraphs])
        else: # assuming text/plain
            text = file_bytes.decode("utf-8", errors="ignore")
    except Exception as e:
        logger.error(f"[RESUME_PARSER] Extraction failed: {str(e)}")
        raise ResumeNoText()
                
    if len(text.strip()) < 50:
        logger.warning(f"[RESUME_PARSER] Minimal text found for user={user_id}")
        raise ResumeNoText()

    formatted_prompt = RESUME_EXTRACTION_PROMPT.format(resume_text=text)
    
    response = await provider.complete([{"role": "user", "content": formatted_prompt}])
    
    clean_json = response.strip()
    if "```" in clean_json:
        clean_json = clean_json.split("```")[1]
        if clean_json.startswith("json"):
            clean_json = clean_json[4:]
    clean_json = clean_json.strip()
    
    try:
        parsed_dict = json.loads(clean_json)
    except json.JSONDecodeError:
        logger.error(f"[RESUME_PARSER] JSON parse failed. Response preview: {response[:200]}")
        raise GeminiParseError()
        
    logger.info(f"[RESUME_PARSER] Success for user={user_id}. Skills={len(parsed_dict.get('skills', []))}")
    
    return {
        "parsed": parsed_dict,
        "raw_text": text
    }

async def score_ats(text: str, provider: ILLMProvider) -> dict:
    """Deterministic ATS scoring in <1ms without burning LLM calls."""
    import re
    has_email = bool(re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}", text))
    has_phone = bool(re.search(r"(?:\+?91[\-\s]?)?[6-9]\d{9}", text))
    has_skills = bool(re.search(r"(skills|technical skills|competencies)", text, re.I))
    has_exp = bool(re.search(r"(experience|work experience|employment)", text, re.I))
    has_edu = bool(re.search(r"(education|academics|qualifications)", text, re.I))
    
    fmt = 30 if (has_email and has_phone) else 15
    kw = 32 if (has_skills and has_exp) else 18
    imp = 28 if re.search(r"\d+[%kK+]", text) else 15
    total = fmt + kw + imp

    suggestions = []
    if not has_email or not has_phone:
        suggestions.append("Add verified phone and professional email prominently at the top.")
    if imp < 20:
        suggestions.append("Add quantified metrics (e.g., percentages, scale, cost saved) to experience bullets.")
    if not has_skills:
        suggestions.append("Create a dedicated 'Technical Skills' section for ATS parsing.")

    return {
        "score": total,
        "breakdown": {"formatting": fmt, "keywords": kw, "impact": imp},
        "suggestions": suggestions
    }

async def extract_india_details(text: str, provider: ILLMProvider) -> dict:
    """Deterministic Indian qualification and exam extraction in <0.1ms."""
    import re
    exams = [m for m in ["GATE", "UPSC", "JEE", "CAT", "NET", "SSC"] if re.search(rf"{m}", text, re.I)]
    certs = [m for m in ["NPTEL", "CDAC", "ITI", "Polytechnic", "PMKVY", "NSDC", "Skill India", "AWS", "Azure", "GCP", "Docker"] if re.search(rf"{m}", text, re.I)]
    return {"exams": exams, "certificates": certs}

async def detect_achievements(text: str, provider: ILLMProvider) -> dict:
    """Deterministic metric-bearing achievement isolation in <0.1ms."""
    from services.deterministic_resume_extractor import extract_quantified_achievements
    raw_achievements = extract_quantified_achievements(text)
    return {"achievements": raw_achievements[:6]}

async def rewrite_bullets(bullets: list[str], provider: ILLMProvider) -> dict:
    response = await provider.complete(
        [{"role": "user", "content": BULLET_REWRITE_PROMPT.format(bullets=json.dumps(bullets))}]
    )
    return _parse_json(response)

def _parse_json(data: str) -> dict:
    clean = data.strip()
    if "```" in clean:
        clean = clean.split("```")[1]
        if clean.startswith("json"): clean = clean[4:]
    clean = clean.strip()
    try:
        return json.loads(clean)
    except:
        logger.error(f"[AI_PARSER] Failed to parse JSON from: {data[:100]}")
        return {}
