"""
Resume parser — extracts text from PDF using pdfplumber,
then matches against a list of common Indian workforce skills.
"""
import pdfplumber
import re
from io import BytesIO
from app.core.logger import get_logger

log = get_logger("PROFILE")

# 150 common skills across sectors in India
SKILL_KEYWORDS = [
    # Tech
    "python", "java", "javascript", "typescript", "c++", "c#", "php", "ruby", "golang", "rust",
    "react", "angular", "vue", "nodejs", "django", "flask", "fastapi", "spring", "sql", "postgresql",
    "mysql", "mongodb", "redis", "elasticsearch", "aws", "azure", "gcp", "docker", "kubernetes",
    "git", "linux", "excel", "word", "powerpoint", "tally", "sap", "erp", "photoshop", "illustrator",
    "autocad", "solidworks", "matlab", "r", "tableau", "power bi", "machine learning", "deep learning",
    "data analysis", "data science", "artificial intelligence", "nlp",
    # Blue collar
    "welding", "plumbing", "electrical wiring", "carpentry", "masonry", "painting", "hvac",
    "mechanical repair", "engine repair", "driving", "heavy vehicle", "forklift", "crane operation",
    "hydraulics", "pneumatics", "tig welding", "mig welding", "arc welding",
    # Trades / Service
    "cooking", "baking", "tailoring", "embroidery", "beauty", "salon", "nursing", "first aid",
    "patient care", "physiotherapy", "accounting", "bookkeeping", "gst", "taxation", "tds",
    "customer service", "sales", "marketing", "digital marketing", "seo", "content writing",
    "social media", "photography", "videography", "event management", "logistics", "supply chain",
    "warehousing", "quality control", "six sigma",
    # Soft skills
    "communication", "leadership", "teamwork", "problem solving", "time management",
    "project management", "negotiation", "training", "teaching",
    # Languages
    "hindi", "english", "punjabi", "marathi", "gujarati", "tamil", "telugu", "kannada", "bengali",
]


def _extract_hints(text: str, pattern: str, context_words: int = 6) -> list[str]:
    """Pull short snippets around matched keyword for hints."""
    results = []
    words = text.split()
    for i, w in enumerate(words):
        if re.search(pattern, w, re.IGNORECASE):
            snippet = " ".join(words[max(0, i-2):i+context_words])
            results.append(snippet[:80])
    return results[:5]  # max 5 hints


def parse_resume(file_bytes: bytes, filename: str) -> dict:
    """
    Extract text from PDF, find skills + education/experience hints.
    Returns dict with raw_text, parsed (skills, education, experience).
    """
    try:
        with pdfplumber.open(BytesIO(file_bytes)) as pdf:
            pages = [page.extract_text() or "" for page in pdf.pages]
            raw_text = "\n".join(pages)
    except Exception as e:
        log.warning(f"pdfplumber failed on {filename}: {e}")
        raw_text = ""

    if not raw_text.strip():
        log.warning(f"Resume PDF has no extractable text (scanned image?): {filename}")

    text_lower = raw_text.lower()
    skills_found = [skill for skill in SKILL_KEYWORDS if skill in text_lower]

    education_hints = _extract_hints(raw_text, r"(b\.?tech|m\.?tech|bsc|msc|ba|mba|diploma|degree|graduate|university|college|school|10th|12th)")
    experience_hints = _extract_hints(raw_text, r"(experience|worked|job|position|role|company|years|months)")

    log.info(f"Resume parsed for file={filename}. Found {len(skills_found)} skills: {skills_found[:8]}")

    return {
        "raw_text": raw_text,
        "parsed": {
            "skills": skills_found,
            "education": education_hints,
            "experience": experience_hints,
        }
    }
