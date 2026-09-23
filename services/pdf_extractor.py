import re
from loguru import logger
from services.pdf.extractor import extract_pdf_content
from services.pdf.section_parser import extract_contact_info, segment_sections

def normalize_text(text: str) -> str:
    """Normalize excess whitespace and bullets while preserving paragraph structure."""
    if not text:
        return ""
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'^[ \t]*[•●○■▪▫‣✓✔\-\*][ \t]*', '• ', text, flags=re.MULTILINE)
    text = re.sub(r'[ \t]{2,}', ' ', text)
    return text.strip()

def extract_resume_bundle(content: bytes) -> dict:
    """Extracts raw text, hyperlinks, contact information, and parsed sections in a single pass."""
    pdf_data = extract_pdf_content(content)
    clean_text = normalize_text(pdf_data["raw_text"])
    contacts = extract_contact_info(clean_text, pdf_data["links"])
    sections = segment_sections(clean_text)

    return {
        "text": clean_text,
        "links": pdf_data["links"],
        "contacts": contacts,
        "sections": sections,
        "page_count": pdf_data["page_count"]
    }

def extract_resume_text(content: bytes) -> str:
    """Primary entry point for backwards-compatible resume text extraction."""
    logger.info("[PDF_EXTRACTOR] Processing PDF content...")
    bundle = extract_resume_bundle(content)
    logger.info(f"[PDF_EXTRACTOR] Complete. Length: {len(bundle['text'])} chars, {len(bundle['links'])} links.")
    return bundle["text"]
