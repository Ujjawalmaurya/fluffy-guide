"""
taxonomy.py — Standard technical, vocational, and digital skill taxonomy and pattern sets for India.
"""
import re
from typing import Dict, List

SKILL_TAXONOMY: Dict[str, str] = {
    # Programming & Tech
    "python": "technical", "javascript": "technical", "typescript": "technical",
    "react": "technical", "reactjs": "technical", "node.js": "technical", "nodejs": "technical",
    "fastapi": "technical", "django": "technical", "flask": "technical", "express": "technical",
    "sql": "technical", "postgresql": "technical", "mysql": "technical", "mongodb": "technical",
    "redis": "technical", "docker": "technical", "kubernetes": "technical", "aws": "technical",
    "azure": "technical", "gcp": "technical", "git": "technical", "github": "technical",
    "linux": "technical", "html": "technical", "css": "technical", "tailwind": "technical",
    "java": "technical", "c++": "technical", "c#": "technical", "php": "technical",
    "machine learning": "technical", "deep learning": "technical", "pytorch": "technical",
    "tensorflow": "technical", "pandas": "technical", "numpy": "technical", "scikit-learn": "technical",
    
    # Data & Analytics
    "power bi": "technical", "tableau": "technical", "excel": "technical", "data analysis": "technical",
    "business analysis": "technical", "etl": "technical", "big data": "technical", "spark": "technical",
    
    # Indian Vocational & Industry Skills
    "iti": "vocational", "polytechnic": "vocational", "autocad": "technical", "cnc": "vocational",
    "plc": "vocational", "welding": "vocational", "electrician": "vocational", "fitter": "vocational",
    "machinist": "vocational", "wiring": "vocational", "tally": "technical", "tally erp 9": "technical",
    "tally prime": "technical", "gst filing": "technical", "solar installation": "vocational",
    "hvac": "vocational", "vehicle maintenance": "vocational", "two wheeler repair": "vocational",
    
    # Soft & Management Skills
    "leadership": "soft", "communication": "soft", "team management": "soft",
    "problem solving": "soft", "client management": "soft", "project management": "soft",
    "scrum": "management", "agile": "management", "negotiation": "soft"
}

VOCATIONAL_PATTERNS: List[str] = [
    r"\bITI\b", r"\bPolytechnic\b", r"\bDiploma\b", r"\bNSDC\b", r"\bPMKVY\b",
    r"\bNPTEL\b", r"\bCDAC\b", r"\bGATE\b", r"\bUPSC\b", r"\bJEE\b", r"\bSkill India\b"
]

ACHIEVEMENT_METRIC_REGEX = re.compile(
    r"(?:\b\d+(?:\.\d+)?%|\b\d+k\+?|\b\d+\s*(?:lakh|crore|million|users|clients|requests|transactions)\b|"
    r"(?:increased|decreased|reduced|improved|boosted|saved|scaled|led|managed)\s+[^\n.]*\b\d+)",
    re.IGNORECASE
)
