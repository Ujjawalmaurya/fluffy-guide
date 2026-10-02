"""
service.py — Suggestions generation coordinator.
Combines concurrent LLM generation (bullets & summary) with deterministic rule sets.
"""
import asyncio
from typing import List, Optional
from loguru import logger

from app.modules.resume_analysis.schemas import (
    StructuredProfile,
    QualityScores,
    SuggestionSet,
)
from app.modules.resume_analysis.suggester.constants import (
    TRANSFERABLE_SKILLS_MAP,
    WEAK_PHRASING_MAP,
)
from app.modules.resume_analysis.suggester.bullet_enhancer import batch_improve_bullets
from app.modules.resume_analysis.suggester.summary_generator import generate_summary


def _detect_transferable_skills(profile: StructuredProfile) -> List[str]:
    detected = []
    skills_str = " ".join([s.name if hasattr(s, "name") else str(s) for s in profile.skills])
    all_text = skills_str.lower()
    for exp in profile.experiences:
        all_text += " " + " ".join(exp.responsibilities).lower()
        all_text += " " + " ".join(exp.achievements).lower()

    for key, val in TRANSFERABLE_SKILLS_MAP.items():
        if key in all_text:
            detected.append(val)
    return list(set(detected))


def _detect_skills_to_reframe(profile: StructuredProfile) -> dict[str, str]:
    skills_to_reframe = {}
    for skill_obj in profile.skills:
        skill = skill_obj.name if hasattr(skill_obj, "name") else str(skill_obj)
        for weak, strong in WEAK_PHRASING_MAP.items():
            if weak.lower() in skill.lower():
                skills_to_reframe[skill] = strong
    return skills_to_reframe


def _detect_india_flags(profile: StructuredProfile) -> List[str]:
    india_flags = []
    if profile.has_photo_mentioned:
        india_flags.append("Remove photo: Modern Indian ATS/HR standards prefer no-photo resumes to avoid bias.")
    if profile.has_caste_religion_info:
        india_flags.append("Remove personal details: Caste, religion, and father's name are not required in professional resumes.")
    return india_flags


async def generate_suggestions(
    profile: StructuredProfile,
    quality_scores: QualityScores,
    target_roles: Optional[List[str]] = None,
) -> SuggestionSet:
    """Generates a complete SuggestionSet for the resume."""
    logger.info("[RESUME_ANALYSIS] Generating suggestions...")

    all_weak_bullets = []
    for exp in profile.experiences:
        for bullet in exp.responsibilities:
            all_weak_bullets.append((bullet, exp.role))

    all_weak_bullets.sort(key=lambda x: len(x[0]))
    worst_bullets = all_weak_bullets[:3]

    role_context = ", ".join(target_roles) if target_roles else None
    weak_bullet_texts = [b[0] for b in worst_bullets]

    bullet_improvements_task = batch_improve_bullets(weak_bullet_texts, role_context)
    summary_task = generate_summary(profile, target_roles)

    bullet_improvements, summary = await asyncio.gather(
        bullet_improvements_task,
        summary_task,
    )

    detected_transferable = _detect_transferable_skills(profile)
    skills_to_reframe = _detect_skills_to_reframe(profile)
    india_flags = _detect_india_flags(profile)

    return SuggestionSet(
        summary_generated=summary,
        bullet_improvements=list(bullet_improvements),
        skills_to_add=[],
        skills_to_reframe=skills_to_reframe,
        sections_to_add=quality_scores.missing_sections,
        india_specific_flags=india_flags,
        transferable_skills_detected=detected_transferable,
    )
