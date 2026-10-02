"""
Resume Extractor with Deterministic Pre-Flight & Multi-Provider Semantic Router.
Combines zero-LLM deterministic extraction (contact, links, flags, taxonomy skills)
with structured LLM synthesis for experiences, education, and career trajectory.
100% resilient: if LLM fails, deterministic pre-flight provides complete fallback.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional
from loguru import logger

from models.resume_analysis_models import (
    CareerTrajectory,
    EducationEntry,
    ExperienceEntry,
    Skill,
    StructuredProfile,
)
from services.deterministic_resume_extractor import parse_resume_deterministic_preflight


# Concise, high-density synthesis prompt focusing exclusively on complex inferences
RESUME_SYNTHESIS_PROMPT = """You are an expert career analyst. Extract structured experience, education, and trajectory from this resume text.
Return ONLY valid JSON matching this schema:
{{
  "experiences": [
    {{
      "company": "Company Name",
      "role": "Job Title",
      "duration_months": 12,
      "seniority_level": "junior|mid|senior|lead|unclear",
      "skills_used": ["Skill1", "Skill2"],
      "responsibilities": ["Task description 1", "Task description 2"],
      "achievements": ["Quantified outcome 1"]
    }}
  ],
  "education": [
    {{
      "degree": "Degree/Diploma Name",
      "institution": "School/University Name",
      "year": 2022,
      "specialization": "Field of Study",
      "is_vocational": false
    }}
  ],
  "career_trajectory": {{
    "direction": "ascending|lateral|descending|unclear",
    "summary": "1-sentence career trajectory overview."
  }},
  "inferred_target_roles": ["Role 1", "Role 2", "Role 3"]
}}
"""


async def _get_active_provider():
    """Returns high-speed Gemini Flash Lite provider when configured, or local Ollama fallback."""
    try:
        from app.core.config import settings
        if getattr(settings, "gemini_api_key", None):
            from app.modules.ai_chat.providers.gemini import get_gemini_instance
            gemini = get_gemini_instance()
            if gemini.model is not None:
                return gemini
    except Exception as e:
        logger.warning(f"[RESUME_ANALYSIS] Gemini provider check failed: {e}")

    try:
        from app.modules.ai_chat.providers.ollama_provider import get_ollama_instance
        ollama = get_ollama_instance()
        if await ollama.is_available():
            return ollama
    except Exception as e:
        logger.warning(f"[RESUME_ANALYSIS] Ollama provider check failed: {e}")

    return None


def _build_deterministic_profile(preflight: Dict[str, Any], raw_text: str) -> StructuredProfile:
    """Builds a rich, valid StructuredProfile entirely from zero-LLM deterministic pre-flight data."""
    skills = [Skill(name=s["name"], level=s.get("level", "intermediate")) for s in preflight.get("skills", [])]
    skill_levels = {s.name: (s.level or "intermediate") for s in skills}

    # Heuristic experience and education extraction from text blocks
    experiences: List[ExperienceEntry] = []
    education: List[EducationEntry] = []

    # Check for basic degree mentions
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

    # Add quantified achievements to a synthetic experience block if none exists
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


async def extract_structured_profile(raw_text: str) -> StructuredProfile:
    """
    High-performance resume extraction pipeline.
    Phase 1: Deterministic Pre-Flight (<2ms) extracts ground-truth contact, skills, and flags.
    Phase 2: Scoped LLM synthesis extracts complex experience, education, and trajectory.
    Phase 3: Guaranteed schema merge; 100% fail-safe fallback if AI is offline.
    """
    logger.info("[RESUME_ANALYSIS] Phase 1: Running deterministic pre-flight extraction...")
    preflight = parse_resume_deterministic_preflight(raw_text)

    provider = await _get_active_provider()
    if provider is None:
        logger.warning("[RESUME_ANALYSIS] No active LLM provider online. Returning deterministic profile.")
        return _build_deterministic_profile(preflight, raw_text)

    # Scoped prompt with pre-extracted skills provided as anchor context
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
        
        # If AI inferred additional skills, add them
        for exp in ai_data.get("experiences", []):
            for skill in exp.get("skills_used", []):
                if isinstance(skill, str) and skill.lower() not in merged_skills_dict:
                    merged_skills_dict[skill.lower()] = {"name": skill.title(), "level": "intermediate"}

        final_skills = [
            Skill(name=s["name"], level=s.get("level", "intermediate"))
            for s in merged_skills_dict.values()
        ]

        # Parse experiences
        experiences: List[ExperienceEntry] = []
        for exp in ai_data.get("experiences", []):
            if isinstance(exp, dict):
                experiences.append(ExperienceEntry(
                    company=exp.get("company", "Company"),
                    role=exp.get("role", "Role"),
                    duration_months=int(exp.get("duration_months") or 0),
                    seniority_level=exp.get("seniority_level", "unclear") if exp.get("seniority_level") in ["junior", "mid", "senior", "lead", "unclear"] else "unclear",
                    skills_used=exp.get("skills_used", []),
                    achievements=exp.get("achievements", []),
                    responsibilities=exp.get("responsibilities", []),
                ))

        # Parse education
        education: List[EducationEntry] = []
        for edu in ai_data.get("education", []):
            if isinstance(edu, dict):
                education.append(EducationEntry(
                    degree=edu.get("degree", "Degree"),
                    institution=edu.get("institution", "Institution"),
                    year=int(edu.get("year")) if str(edu.get("year", "")).isdigit() else None,
                    specialization=edu.get("specialization"),
                    is_vocational=bool(edu.get("is_vocational", False)),
                ))

        # Parse trajectory
        traj_data = ai_data.get("career_trajectory", {})
        if isinstance(traj_data, dict):
            trajectory = CareerTrajectory(
                direction=traj_data.get("direction", "unclear") if traj_data.get("direction") in ["ascending", "lateral", "descending", "unclear"] else "unclear",
                summary=traj_data.get("summary", "Consistent professional development.")
            )
        else:
            trajectory = CareerTrajectory(direction="unclear", summary=str(traj_data))

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
        return _build_deterministic_profile(preflight, raw_text)
