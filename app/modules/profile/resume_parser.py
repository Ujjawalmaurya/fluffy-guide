# [RESUME_PARSER] Extracts structured career data from resume PDF.
# Uses pdfplumber for text extraction, Gemini (Flash/Pro) and Groq for intelligence.
# Returns structured JSON — never uses keyword lists.

import io
import json
import pdfplumber
import docx
from loguru import logger

from app.modules.ai_chat.providers.gemini import GeminiProvider
from app.shared.exceptions import ResumeNoText, GeminiParseError

# Optimized prompt for lower token usage and deeper insights
RESUME_EXTRACTION_PROMPT = """Extract deep career insights from the resume below.
Return ONLY valid JSON. No markdown.

Fields:
- skills: list of {name, category, proficiency_label, years_used}
- experience_level: Entry|Junior|Mid|Senior|Expert
- strengths: list of strings
- weaknesses: list of strings (areas for improvement)
- career_suggestions: list of strings (suitable roles in India)
- skill_gap_analysis: sentence on what's missing for target roles
- education: list of {degree, institution, year}
- experience: list of {title, company, duration}

Resume:
{resume_text}"""

ATS_SCORING_PROMPT = """Score the resume below for ATS compatibility.
Return ONLY valid JSON. No markdown.

Fields:
- score: int (0-100)
- breakdown: {formatting: 0-33, keywords: 0-33, impact: 0-34}
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
- achievements: list of {title: "Short description", impact: "Quantified metric"}

Resume:
{resume_text}"""

BULLET_REWRITE_PROMPT = """Rewrite the following resume bullets to be more impactful and result-oriented.
Return ONLY valid JSON. No markdown.

Input Bullets:
{bullets}

Return as:
{rewritten_bullets: ["new bullet 1", "new bullet 2", ...]}"""

async def parse_resume(file_bytes: bytes, filename: str, content_type: str, user_id: str,
                       gemini_provider: GeminiProvider) -> dict:
    
    logger.info(f"[RESUME_PARSER] Extracting text for user={user_id} file={filename}")
    text = ""
    
    try:
        if filename.lower().endswith(".pdf"):
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
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
        
    # Token optimization: limit to 4000 chars for analysis
    if len(text) > 4000:
        text = text[:4000]
        logger.info("[RESUME_PARSER] Truncated to 4000 chars for efficiency")
        
    formatted_prompt = RESUME_EXTRACTION_PROMPT.format(resume_text=text)
    
    # Retry logic is handled inside gemini_provider.complete (backoff)
    response = await gemini_provider.complete([{"role": "user", "content": formatted_prompt}])
    
    # Clean JSON output
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

async def score_ats(text: str, gemini_provider: GeminiProvider) -> dict:
    # Use gemini-1.5-pro for better scoring reasoning
    response = await gemini_provider.complete(
        [{"role": "user", "content": ATS_SCORING_PROMPT.format(resume_text=text)}],
        model_name="gemini-1.5-pro"
    )
    return _parse_json(response)

async def extract_india_details(text: str, gemini_provider: GeminiProvider) -> dict:
    response = await gemini_provider.complete(
        [{"role": "user", "content": INDIA_QUALIFICATIONS_PROMPT.format(resume_text=text)}]
    )
    return _parse_json(response)

async def detect_achievements(text: str, groq_provider) -> dict:
    # groq_provider is usually faster for this type of detection
    response = await groq_provider.complete(
        [{"role": "user", "content": ACHIEVEMENT_DETECTION_PROMPT.format(resume_text=text)}]
    )
    return _parse_json(response)

async def rewrite_bullets(bullets: list[str], groq_provider) -> dict:
    response = await groq_provider.complete(
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
