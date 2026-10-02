"""
llm_extractor.py — Scoped LLM resume synthesis and schema merger.
Merges deterministic ground truth with LLM inferred experiences and trajectories.
"""
from __future__ import annotations

import json
from typing import List
from loguru import logger

from app.modules.resume_analysis.schemas import (
    CareerTrajectory,
    EducationEntry,
    ExperienceEntry,
    Skill,
    StructuredProfile,
)
from app.modules.resume_analysis.prompts import RESUME_SYNTHESIS_PROMPT
from app.modules.resume_analysis.provider import get_active_provider
from app.modules.resume_analysis.deterministic import (
    build_deterministic_profile,
    parse_resume_deterministic_preflight,
)


def _parse_ai_experiences(ai_experiences: list) -> List[ExperienceEntry]:
    experiences: List[ExperienceEntry] = []
    for exp in ai_experiences:
        if isinstance(exp, dict):
            seniority = exp.get("seniority_level", "unclear")
            valid_seniority = seniority if seniority in ["junior", "mid", "senior", "lead", "unclear"] else "unclear"
            experiences.append(ExperienceEntry(
                company=exp.get("company", "Company"),
                role=exp.get("role", "Role"),
                duration_months=int(exp.get("duration_months") or 0),
                seniority_level=valid_seniority,
                skills_used=exp.get("skills_used", []),
                achievements=exp.get("achievements", []),
                responsibilities=exp.get("responsibilities", []),
            ))
    return experiences


def _parse_ai_education(ai_education: list) -> List[EducationEntry]:
    education: List[EducationEntry] = []
    for edu in ai_education:
        if isinstance(edu, dict):
            year_val = edu.get("year")
            education.append(EducationEntry(
                degree=edu.get("degree", "Degree"),
                institution=edu.get("institution", "Institution"),
                year=int(year_val) if str(year_val or "").isdigit() else None,
                specialization=edu.get("specialization"),
                is_vocational=bool(edu.get("is_vocational", False)),
            ))
    return education


def _parse_ai_trajectory(traj_data: any) -> CareerTrajectory:
    if isinstance(traj_data, dict):
        direction = traj_data.get("direction", "unclear")
        valid_dir = direction if direction in ["ascending", "lateral", "descending", "unclear"] else "unclear"
        return CareerTrajectory(
            direction=valid_dir,
            summary=traj_data.get("summary", "Consistent professional development.")
        )
    return CareerTrajectory(direction="unclear", summary=str(traj_data))


async def extract_structured_profile(raw_text: str) -> StructuredProfile:
    """
    High-performance resume extraction pipeline.
    Phase 1: Deterministic Pre-Flight (<2ms) extracts ground-truth contact, skills, and flags.
    Phase 2: Scoped LLM synthesis extracts complex experience, education, and trajectory.
    Phase 3: Guaranteed schema merge; 100% fail-safe fallback if AI is offline.
    """
    logger.info("[RESUME_ANALYSIS] Phase 1: Running deterministic pre-flight extraction...")
    preflight = parse_resume_deterministic_preflight(raw_text)

    provider = await get_active_provider()
    if provider is None:
        logger.warning("[RESUME_ANALYSIS] No active LLM provider online. Returning deterministic profile.")
        return build_deterministic_profile(preflight, raw_text)

    known_skills = [s["name"] for s in preflight.get("skills", [])]
    user_prompt = (
        f"Pre-extracted Verified Skills: {', '.join(known_skills) if known_skills else 'None'}\n\n"
        f"Resume Text:\n{raw_text[:8000]}"
    )

    messages = [
        {"role": "system", "content": RESUME_SYNTHESIS_PROMPT},
        {"role": "user", "content": user_prompt}
    ]

    logger.info(f"[RESUME_ANALYSIS] Phase 2: Calling LLM provider ({provider.__class__.__name__})...")
    try:
        if hasattr(provider, "complete_json"):
            ai_data = await provider.complete_json(messages, temperature=0.2, max_tokens=2000)
        else:
            raw_res = await provider.complete(messages, temperature=0.2)
            clean = raw_res.strip()
            if "```" in clean:
                clean = clean.split("```")[1]
                if clean.startswith("json"):
                    clean = clean[4:]
            ai_data = json.loads(clean.strip())

        # Phase 3: Merge deterministic ground truth with LLM inferences
        merged_skills_dict = {s["name"].lower(): s for s in preflight.get("skills", [])}
        for exp in ai_data.get("experiences", []):
            for skill in exp.get("skills_used", []):
                if isinstance(skill, str) and skill.lower() not in merged_skills_dict:
                    merged_skills_dict[skill.lower()] = {"name": skill.title(), "level": "intermediate"}

        final_skills = [
            Skill(name=s["name"], level=s.get("level", "intermediate"))
            for s in merged_skills_dict.values()
        ]

        experiences = _parse_ai_experiences(ai_data.get("experiences", []))
        education = _parse_ai_education(ai_data.get("education", []))
        trajectory = _parse_ai_trajectory(ai_data.get("career_trajectory", {}))

        inferred_roles = ai_data.get("inferred_target_roles", [])
        if not isinstance(inferred_roles, list) or not inferred_roles:
            inferred_roles = ["Technical Specialist"]

        profile = StructuredProfile(
            full_name=preflight.get("full_name"),
            contact_email=preflight.get("contact_email"),
            contact_phone=preflight.get("contact_phone"),
            has_photo_mentioned=preflight.get("has_photo_mentioned", False),
            has_caste_religion_info=preflight.get("has_caste_religion_info", False),
            skills=final_skills,
            skill_levels={s.name: (s.level or "intermediate") for s in final_skills},
            soft_skills_inferred=preflight.get("soft_skills_inferred", []),
            experiences=experiences,
            education=education,
            career_trajectory=trajectory,
            has_linkedin=preflight.get("has_linkedin", False),
            has_github=preflight.get("has_github", False),
            has_summary_section=preflight.get("has_summary_section", False),
            inferred_target_roles=inferred_roles,
        )
        logger.info(f"[RESUME_ANALYSIS] Complete. Skills={len(profile.skills)}, Exps={len(profile.experiences)}")
        return profile

    except Exception as e:
        logger.error(f"[RESUME_ANALYSIS] LLM synthesis failed ({e}). Falling back to deterministic profile.")
        return build_deterministic_profile(preflight, raw_text)
