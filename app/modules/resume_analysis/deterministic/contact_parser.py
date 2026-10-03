"""
contact_parser.py — Zero-hallucination contact information and profile link parser.
"""
import re
from typing import Any, Dict


def extract_contact_info(text: str) -> Dict[str, Any]:
    """Extracts contact coordinates and URLs deterministically with zero hallucination."""
    email_match = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b", text)
    phone_match = re.search(r"(?:\+?91[\-\s]?)?[6-9]\d{9}\b", text)
    linkedin_match = re.search(r"(?:https?://)?(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_\-\.\/]+", text, re.IGNORECASE)
    github_match = re.search(r"(?:https?://)?(?:www\.)?github\.com/[a-zA-Z0-9_\-\.\/]+", text, re.IGNORECASE)

    # Heuristic full name extraction from the top of the resume
    full_name = None
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for line in lines[:5]:
        lower_line = line.lower()
        if (
            len(line) < 40
            and not any(k in lower_line for k in ["resume", "cv", "curriculum", "email", "phone", "contact", "http", "www", "@"])
            and re.match(r"^[A-Za-z\s\.]+$", line)
        ):
            full_name = line
            break

    return {
        "full_name": full_name or "Candidate",
        "contact_email": email_match.group(0) if email_match else None,
        "contact_phone": phone_match.group(0) if phone_match else None,
        "has_linkedin": bool(linkedin_match),
        "has_github": bool(github_match),
        "linkedin_url": linkedin_match.group(0) if linkedin_match else None,
        "github_url": github_match.group(0) if github_match else None,
    }
