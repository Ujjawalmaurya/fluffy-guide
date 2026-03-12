# [RESUME_PARSER] Extracts structured career data from resume PDF.
# Uses pdfplumber for text extraction, Gemini Flash for intelligence.
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
