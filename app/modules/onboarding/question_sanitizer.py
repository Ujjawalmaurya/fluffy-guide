import re

OPEN_ENDED_MARKERS = [
    r'\bdescribe\b',
    r'\bexplain\b',
    r'\bdiscuss\b',
    r'\bdetail\b',
    r'\bwrite\b',
    r'\bshare\b',
    r'\btell\s+(?:me|us)\b',
    r'\bin\s+(?:your\s+own|a\s+few|some|short|brief)\s+words\b',
    r'\banswer\s+(?:me\s+)?in\s+(?:some|a\s+few|your\s+own|short|brief)\s+words\b',
    r'\bwhat\s+(?:are|is|were|kind|types|tools|projects|work|skills|experience)\b',
    r'\bhow\s+(?:do|did|would|have)\s+you\b',
    r'\bgive\s+(?:an?\s+)?example\b',
]
OPEN_ENDED_REGEX = re.compile('|'.join(OPEN_ENDED_MARKERS), re.IGNORECASE)

RATING_MARKERS = [
    r'\brate\s+(?:your|yourself|on)\b',
    r'\bscale\s+(?:of\s+)?1\s*(?:to|-)\s*5\b',
    r'\b(?:1\s*(?:to|-)\s*5)\s+scale\b',
    r'\bon\s+a\s+scale\b',
    r'\bfrom\s+1\s+(?:to|-)\s+5\b',
]
RATING_REGEX = re.compile('|'.join(RATING_MARKERS), re.IGNORECASE)


def sanitize_question(q: dict) -> dict:
    """Ensures semantic alignment between question text and answer input type."""
    text = q.get("question") or q.get("question_text") or ""
    raw_type = (q.get("type") or q.get("question_type") or "").lower().strip()
    options = q.get("options")
    if not isinstance(options, list):
        options = []

    is_open_ended = bool(OPEN_ENDED_REGEX.search(text))
    is_explicit_rating = bool(RATING_REGEX.search(text))

    if is_open_ended and not is_explicit_rating:
        q_type = "text"
        options = []
    elif is_explicit_rating:
        q_type = "rating"
        options = ["1", "2", "3", "4", "5"]
    elif raw_type == "mcq" and len(options) >= 2:
        q_type = "mcq"
    elif raw_type == "rating" and is_explicit_rating:
        q_type = "rating"
        options = ["1", "2", "3", "4", "5"]
    else:
        q_type = "text"
        options = []

    res = dict(q)
    res["type"] = q_type
    res["question_type"] = q_type
    res["options"] = options
    return res


def sanitize_question_list(questions: list[dict]) -> list[dict]:
    """Sanitize a list of generated questions."""
    return [sanitize_question(q) for q in questions if isinstance(q, dict)]
