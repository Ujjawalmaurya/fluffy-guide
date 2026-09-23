import re

OPEN_ENDED_MARKERS = [
    r'\bdescribe\b', r'\bexplain\b', r'\bin\s+(?:your\s+own|a\s+few)\s+words\b',
    r'\btell\s+us\b', r'\bwhat\s+(?:are|is|were)\s+your\b', r'\bshare\s+your\b',
    r'\bhow\s+do\s+you\s+(?:handle|approach|perform|do)\b', r'\bdetail\b', r'\bwrite\b'
]
OPEN_ENDED_REGEX = re.compile('|'.join(OPEN_ENDED_MARKERS), re.IGNORECASE)

RATING_MARKERS = [
    r'\brate\b', r'\bscale\s+(?:of\s+)?1\s*(?:to|-)\s*5\b',
    r'\bhow\s+(?:comfortable|confident|proficient|familiar)\b',
    r'\brating\b', r'\blevel\s+of\s+comfort\b'
]
RATING_REGEX = re.compile('|'.join(RATING_MARKERS), re.IGNORECASE)

def sanitize_question(q: dict) -> dict:
    """Ensures semantic alignment between question text and answer input type."""
    text = q.get("question") or q.get("question_text") or ""
    q_type = (q.get("type") or q.get("question_type") or "text").lower()
    options = q.get("options") or []

    is_open_ended = bool(OPEN_ENDED_REGEX.search(text))
    is_explicit_rating = bool(RATING_REGEX.search(text))

    # Fix: Open-ended question wrongly labeled as rating or MCQ
    if is_open_ended and not is_explicit_rating:
        q_type = "text"
        options = []
    # Fix: Rating question missing proper scale options
    elif is_explicit_rating or q_type == "rating":
        q_type = "rating"
        options = ["1", "2", "3", "4", "5"]
    # Fix: MCQ without choices falls back to text
    elif q_type == "mcq" and (not isinstance(options, list) or len(options) < 2):
        q_type = "text"
        options = []

    res = dict(q)
    if "type" in res:
        res["type"] = q_type
        res["options"] = options
    if "question_type" in res:
        res["question_type"] = q_type
        res["options"] = options

    return res

def sanitize_question_list(questions: list[dict]) -> list[dict]:
    """Sanitize a list of generated questions."""
    return [sanitize_question(q) for q in questions if isinstance(q, dict)]
