import os
import pymupdf
from loguru import logger


def _sort_blocks_layout_aware(blocks: list) -> list:
    """
    Sorts blocks preserving natural reading order.
    Separates full-width header/footer spans from multi-column body blocks.
    """
    text_blocks = [b for b in blocks if len(b) >= 7 and b[6] == 0 and b[4].strip()]
    if not text_blocks:
        return []

    min_x = min(b[0] for b in text_blocks)
    max_x = max(b[2] for b in text_blocks)
    page_width = max_x - min_x
    if page_width <= 0:
        return text_blocks

    midpoint = min_x + (page_width / 2.0)

    # Detect multi-column structures
    left_blocks = [b for b in text_blocks if b[2] <= midpoint + 20 and b[0] < midpoint]
    right_blocks = [b for b in text_blocks if b[0] >= midpoint - 20 and b[2] > midpoint]
    spanning_blocks = [b for b in text_blocks if b[0] < midpoint - 20 and b[2] > midpoint + 20]

    is_multi_column = len(left_blocks) >= 2 and len(right_blocks) >= 2

    if not is_multi_column:
        text_blocks.sort(key=lambda b: (round(b[1], 1), round(b[0], 1)))
        return text_blocks

    # Partition vertically by spanning blocks, ordering left before right in each band
    ordered_result = []
    spanning_sorted = sorted(spanning_blocks, key=lambda b: b[1])
    current_y = min(b[1] for b in text_blocks) - 1.0

    for span_b in spanning_sorted:
        slice_left = [b for b in left_blocks if current_y <= b[1] < span_b[1]]
        slice_right = [b for b in right_blocks if current_y <= b[1] < span_b[1]]

        slice_left.sort(key=lambda b: (b[1], b[0]))
        slice_right.sort(key=lambda b: (b[1], b[0]))

        ordered_result.extend(slice_left)
        ordered_result.extend(slice_right)
        ordered_result.append(span_b)
        current_y = span_b[3]

    tail_left = [b for b in left_blocks if b[1] >= current_y]
    tail_right = [b for b in right_blocks if b[1] >= current_y]
    tail_left.sort(key=lambda b: (b[1], b[0]))
    tail_right.sort(key=lambda b: (b[1], b[0]))
    ordered_result.extend(tail_left)
    ordered_result.extend(tail_right)

    captured_ids = set(id(b) for b in ordered_result)
    leftovers = [b for b in text_blocks if id(b) not in captured_ids]
    if leftovers:
        leftovers.sort(key=lambda b: (b[1], b[0]))
        ordered_result.extend(leftovers)

    return ordered_result


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
        sorted_blocks = _sort_blocks_layout_aware(blocks)

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
