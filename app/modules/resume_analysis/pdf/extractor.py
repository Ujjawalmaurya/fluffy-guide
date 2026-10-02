"""
extractor.py — High-speed PyMuPDF extraction engine with layout-aware column de-jumbling.
"""
import os
import pymupdf
from loguru import logger
from app.modules.resume_analysis.pdf.block_sorter import sort_blocks_layout_aware


def extract_pdf_content(content: bytes) -> dict:
    """
    High-speed PyMuPDF extraction engine with layout-aware column de-jumbling.
    Extracts text, annotations, and document metadata.
    """
    try:
        doc = pymupdf.open(stream=content, filetype="pdf")
    except Exception as e:
        logger.error(f"[PDF_EXTRACTOR] Failed to open PDF stream: {e}")
        return {"raw_text": "", "links": [], "page_count": 0}

    extracted_pages = []
    extracted_links = []

    for page in doc:
        try:
            for link in page.get_links():
                uri = link.get("uri")
                if uri and uri.startswith(("http://", "https://", "mailto:")):
                    extracted_links.append(uri)
        except Exception:
            pass

        blocks = page.get_text("blocks", sort=False)
        sorted_blocks = sort_blocks_layout_aware(blocks)

        page_lines = [b[4].strip() for b in sorted_blocks if b[4].strip()]
        page_text = "\n\n".join(page_lines)
        if page_text:
            extracted_pages.append(page_text)

    # Scanned PDF check: Only trigger OCR if entire document produced virtually no text
    total_len = sum(len(p) for p in extracted_pages)
    if total_len < 60 and len(doc) > 0 and os.path.exists("/usr/share/tessdata/eng.traineddata"):
        try:
            ocr_pages = []
            for page in doc:
                ocr_page = page.get_textpage_ocr(language="eng", dpi=150)
                ocr_text = page.get_text("text", textpage=ocr_page).strip()
                if ocr_text:
                    ocr_pages.append(ocr_text)
            if sum(len(p) for p in ocr_pages) > total_len:
                extracted_pages = ocr_pages
        except Exception:
            pass

    doc.close()

    full_text = "\n\n--- PAGE BREAK ---\n\n".join(extracted_pages).strip()
    return {
        "raw_text": full_text,
        "links": list(dict.fromkeys(extracted_links)),
        "page_count": len(extracted_pages)
    }
