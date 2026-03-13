import io
import fitz  # PyMuPDF
import pdfplumber
import pytesseract
from PIL import Image
from loguru import logger
import re

def normalize_text(text: str) -> str:
    """
    Cleans up whitespace, normalizes bullets, and merges lines.
    """
    if not text:
        return ""
    
    # Replace multiple newlines with a marker, then clean up
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    # Normalize bullet points (common variations to a standard dot)
    text = re.sub(r'^[ \t]*[•●○■▪▫‣✓✔\-\*][ \t]*', '• ', text, flags=re.MULTILINE)
    
    # Remove excessive horizontal whitespace
    text = re.sub(r'[ \t]{2,}', ' ', text)
    
    # Strip leading/trailing whitespace per line
    lines = [line.strip() for line in text.split('\n')]
    
    return '\n'.join(lines).strip()

def extract_text_via_fitz(content: bytes) -> str:
    """
    Stage 1: Fast and robust text extraction using PyMuPDF.
    """
    try:
        doc = fitz.open(stream=content, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text("text") + "\n"
        return text.strip()
    except Exception as e:
        logger.error(f"[PDF_EXTRACTOR] PyMuPDF failed: {e}")
        return ""

def extract_text_via_pdfplumber(content: bytes) -> str:
    """
    Stage 2: Fallback to pdfplumber for better layout handling if fitz fails or is thin.
    """
    try:
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip()
    except Exception as e:
        logger.error(f"[PDF_EXTRACTOR] pdfplumber failed: {e}")
        return ""

def extract_text_via_ocr(content: bytes) -> str:
    """
    Stage 3: OCR fallback for scanned images using Tesseract.
    """
    try:
        # Convert PDF to images using fitz for OCR
        doc = fitz.open(stream=content, filetype="pdf")
        full_text = ""
        for page in doc:
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2)) # Higher DPI for OCR
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            page_text = pytesseract.image_to_string(img)
            full_text += page_text + "\n"
        return full_text.strip()
    except Exception as e:
        logger.error(f"[PDF_EXTRACTOR] OCR failed: {e}. Ensure Tesseract is installed.")
        return ""

def extract_resume_text(content: bytes) -> str:
    """
    Main entry point for robust PDF text extraction.
    """
    logger.info("[PDF_EXTRACTOR] starting multi-stage extraction...")
    
    # Stage 1: PyMuPDF
    text = extract_text_via_fitz(content)
    
    # Stage 2: pdfplumber fallback (if text is very short/missing)
    if len(text.strip()) < 100:
        logger.info("[PDF_EXTRACTOR] text thin or missing via fitz, trying pdfplumber...")
        plumber_text = extract_text_via_pdfplumber(content)
        if len(plumber_text) > len(text):
            text = plumber_text
            
    # Stage 3: OCR fallback
    if len(text.strip()) < 100:
        logger.warning("[PDF_EXTRACTOR] no text extraction successful, falling back to OCR...")
        text = extract_text_via_ocr(content)
        
    # Result normalization
    clean_text = normalize_text(text)
    
    logger.info(f"[PDF_EXTRACTOR] extraction complete. Length: {len(clean_text)}")
    return clean_text
