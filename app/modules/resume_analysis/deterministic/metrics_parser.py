"""
metrics_parser.py — Quantified metrics and taxonomy skill extraction.
"""
import re
from typing import Dict, List, Set, Tuple
from app.modules.resume_analysis.deterministic.taxonomy import SKILL_TAXONOMY, ACHIEVEMENT_METRIC_REGEX


def extract_skills_from_taxonomy(text: str) -> Tuple[List[Dict[str, str]], List[str]]:
    """Scans raw resume against taxonomy to extract verified hard and soft skills."""
    lower = text.lower()
    detected_hard: List[Dict[str, str]] = []
    detected_soft: List[str] = []
    seen: Set[str] = set()

    for skill_name, category in SKILL_TAXONOMY.items():
        pattern = r"\b" + re.escape(skill_name) + r"\b"
        if re.search(pattern, lower):
            clean_display = skill_name.title() if len(skill_name) > 4 else skill_name.upper()
            if clean_display.lower() in seen:
                continue
            seen.add(clean_display.lower())

            if category == "soft":
                detected_soft.append(clean_display)
            else:
                # Infer level based on context signals
                level = "intermediate"
                if re.search(rf"\b(lead|architect|senior|expert|advanced)\b[^\n]*\b{re.escape(skill_name)}\b", lower) or \
                   re.search(rf"\b{re.escape(skill_name)}\b[^\n]*\b(advanced|expert)\b", lower):
                    level = "advanced"
                elif re.search(rf"\b(beginner|basic|familiar|learning)\b[^\n]*\b{re.escape(skill_name)}\b", lower) or \
                     re.search(rf"\b{re.escape(skill_name)}\b[^\n]*\b(beginner|basic)\b", lower):
                    level = "beginner"

                detected_hard.append({"name": clean_display, "level": level})

    return detected_hard, detected_soft


def extract_quantified_achievements(text: str) -> List[Dict[str, str]]:
    """Isolates metric-bearing achievement statements from resume bullet points."""
    achievements: List[Dict[str, str]] = []
    lines = text.splitlines()

    for line in lines:
        cleaned = line.strip().lstrip("-*•> ")
        if len(cleaned) < 15 or len(cleaned) > 250:
            continue

        metric_match = ACHIEVEMENT_METRIC_REGEX.search(cleaned)
        if metric_match:
            achievements.append({
                "title": cleaned[:60] + "..." if len(cleaned) > 60 else cleaned,
                "impact": metric_match.group(0),
                "full_bullet": cleaned
            })

    return achievements
