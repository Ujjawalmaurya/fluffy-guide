"""
flags_parser.py — Indian regulatory flags, demographic bias detection, and vocational pattern parser.
"""
import re
from typing import Any, Dict
from app.modules.resume_analysis.deterministic.taxonomy import VOCATIONAL_PATTERNS


def extract_indian_regulatory_flags(text: str) -> Dict[str, Any]:
    """Detects ATS compliance, cultural biases, and vocational credentials in Indian resumes."""
    lower = text.lower()
    
    photo_present = bool(re.search(r"\b(photo|photograph|passport size photo|passport photo)\b", lower))
    
    caste_religion_present = bool(
        re.search(
            r"\b(caste|religion|hindu|muslim|christian|sikh|sc/st|obc|marital status|married|unmarried|single|father'?s name|date of birth|dob)\b",
            lower
        )
    )

    detected_vocational = []
    for pattern in VOCATIONAL_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            detected_vocational.extend(matches)

    return {
        "has_photo_mentioned": photo_present,
        "has_caste_religion_info": caste_religion_present,
        "vocational_qualifications": sorted(list(set(detected_vocational))),
    }
