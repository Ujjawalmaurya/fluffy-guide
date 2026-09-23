import pymupdf
import os
from loguru import logger

def _sort_blocks_by_column(blocks: list) -> list:
    """Sort text blocks by column before vertical position to prevent 2-column layout interleaving."""
    if not blocks:
        return []
    
    # Text blocks only: (x0, y0, x1, y1, text, block_no, block_type) where block_type == 0
    text_blocks = [b for b in blocks if len(b) >= 7 and b[6] == 0 and b[4].strip()]
    if not text_blocks:
        return []

    min_x = min(b[0] for b in text_blocks)
    max_x = max(b[2] for b in text_blocks)
    page_width = max_x - min_x
    
    midpoint = min_x + (page_width / 2)
    left_col = [b for b in text_blocks if b[0] < midpoint and b[2] <= midpoint + 30]
    right_col = [b for b in text_blocks if b[0] >= midpoint - 30]

    if len(left_col) >= 2 and len(right_col) >= 2 and (len(left_col) + len(right_col)) >= len(text_blocks) * 0.7:
        left_col.sort(key=lambda b: (b[1], b[0]))
        right_col.sort(key=lambda b: (b[1], b[0]))
        return left_col + right_col

    text_blocks.sort(key=lambda b: (b[1], b[0]))
    return text_blocks

def extract_pdf_content(content: bytes) -> dict:
    """
    High-speed PDF extractor. Preserves layout, detects columns, and extracts hyperlinks.
    Returns dict with raw_text, links, and page_count.
    """
    try:
        doc = pymupdf.open(stream=content, filetype="pdf")
    except Exception as e:
        logger.error(f"[PDF_EXTRACTOR] Failed to open PDF: {e}")
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
        sorted_blocks = _sort_blocks_by_column(blocks)
        
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
