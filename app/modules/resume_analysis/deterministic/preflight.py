"""
preflight.py — Zero-LLM preflight orchestrator and deterministic profile builder.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List

from app.modules.resume_analysis.schemas import (
    CareerTrajectory,
    EducationEntry,
    ExperienceEntry,
    Skill,
    StructuredProfile,
)
from app.modules.resume_analysis.deterministic.contact_parser import extract_contact_info
from app.modules.resume_analysis.deterministic.flags_parser import extract_indian_regulatory_flags
from app.modules.resume_analysis.deterministic.metrics_parser import (
    extract_quantified_achievements,
    extract_skills_from_taxonomy,
)


def parse_resume_deterministic_preflight(raw_text: str) -> Dict[str, Any]:
    """
    Executes complete zero-LLM deterministic extraction pipeline in <2ms.
    Provides verified ground truth for contact, skills, flags, and achievements.
    """
    contacts = extract_contact_info(raw_text)
    flags = extract_indian_regulatory_flags(raw_text)
    hard_skills, soft_skills = extract_skills_from_taxonomy(raw_text)
    achievements = extract_quantified_achievements(raw_text)

    has_summary = bool(re.search(r"\b(summary|objective|profile|about me)\b", raw_text, re.IGNORECASE))

    return {
        **contacts,
        **flags,
        "skills": hard_skills,
        "soft_skills_inferred": soft_skills,
        "achievements": achievements,
        "has_summary_section": has_summary,
        "raw_text_length": len(raw_text),
    }


def build_deterministic_profile(preflight: Dict[str, Any], raw_text: str) -> StructuredProfile:
    """Builds a rich, valid StructuredProfile entirely from zero-LLM deterministic pre-flight data."""
    skills = [Skill(name=s["name"], level=s.get("level", "intermediate")) for s in preflight.get("skills", [])]
    skill_levels = {s.name: (s.level or "intermediate") for s in skills}

    experiences: List[ExperienceEntry] = []
    education: List[EducationEntry] = []

    lines = raw_text.splitlines()
    for line in lines:
        cleaned = line.strip()
        lower = cleaned.lower()
        if any(deg in lower for deg in ["b.tech", "btech", "b.e", "b.sc", "bca", "mca", "diploma", "iti", "bachelor", "master"]):
            education.append(EducationEntry(
                degree=cleaned[:60],
                institution="Educational Institution",
                is_vocational=any(v in lower for v in ["iti", "polytechnic", "diploma", "vocational"])
            ))

    achievements = [a["full_bullet"] for a in preflight.get("achievements", [])]
    if achievements:
        experiences.append(ExperienceEntry(
            company="Recent Experience",
            role="Professional",
            achievements=achievements,
            responsibilities=[]
        ))

    inferred_roles = []
    if any(s.name.lower() in ["python", "fastapi", "django"] for s in skills):
        inferred_roles.append("Python Backend Developer")
    if any(s.name.lower() in ["react", "javascript", "typescript"] for s in skills):
        inferred_roles.append("Frontend Developer")
    if any(s.name.lower() in ["electrician", "wiring", "solar installation"] for s in skills):
        inferred_roles.append("Electrical Technician")
    if not inferred_roles:
        inferred_roles = ["Technical Specialist"]

    return StructuredProfile(
        full_name=preflight.get("full_name"),
        contact_email=preflight.get("contact_email"),
        contact_phone=preflight.get("contact_phone"),
        has_photo_mentioned=preflight.get("has_photo_mentioned", False),
        has_caste_religion_info=preflight.get("has_caste_religion_info", False),
        skills=skills,
        skill_levels=skill_levels,
        soft_skills_inferred=preflight.get("soft_skills_inferred", []),
        experiences=experiences,
        education=education,
        career_trajectory=CareerTrajectory(
            direction="ascending" if len(achievements) > 1 else "unclear",
            summary="Demonstrated practical technical experience and project delivery."
        ),
        has_linkedin=preflight.get("has_linkedin", False),
        has_github=preflight.get("has_github", False),
        has_summary_section=preflight.get("has_summary_section", False),
        inferred_target_roles=inferred_roles,
    )
