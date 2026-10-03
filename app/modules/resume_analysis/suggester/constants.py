"""
constants.py — Rule-based skill phrasing and transferable skill mappings for India.
"""
from typing import Dict

TRANSFERABLE_SKILLS_MAP: Dict[str, str] = {
    "route planning": "logistics coordination",
    "cash handling": "financial accountability",
    "customer dealing": "client relationship management",
    "machine operation": "technical equipment proficiency",
    "team supervision": "team leadership",
}

WEAK_PHRASING_MAP: Dict[str, str] = {
    "MS Office": "Microsoft Office Suite (Excel, Word, PowerPoint)",
    "basic computer": "Computer Proficiency",
    "internet browsing": "Digital Literacy",
    "tally": "Tally ERP 9",
    "driving": "Commercial Vehicle Operation",
}
