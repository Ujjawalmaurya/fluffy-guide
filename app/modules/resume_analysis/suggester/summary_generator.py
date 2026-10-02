"""
summary_generator.py — Generates professional 3-line resume summaries via active LLM.
"""
from typing import List, Optional
from loguru import logger

from app.modules.resume_analysis.schemas import StructuredProfile
from app.modules.resume_analysis.provider import get_active_provider


async def generate_summary(profile: StructuredProfile, target_roles: Optional[List[str]] = None) -> str:
    """Uses active LLM provider (Ollama / Gemini) to generate a concise professional summary."""
    name = profile.full_name or "Professional"
    skills_list = [s.name if hasattr(s, "name") else str(s) for s in profile.skills[:5]]
    skills = ", ".join(skills_list)
    total_months = sum(exp.duration_months for exp in profile.experiences)
    years = total_months // 12

    provider = await get_active_provider()
    if provider is None:
        return f"Results-driven professional with strong expertise in {skills}."

    prompt = (
        f"Generate a 3-line professional resume summary for this candidate. "
        f"Name: {name}. Experience: {years} years. Top skills: {skills}. "
        f"Target roles: {', '.join(target_roles) if target_roles else 'general'}. "
        f"Make it confident, specific, and suitable for Indian job market. Return only the 3 lines."
    )

    try:
        summary = await provider.complete([{"role": "user", "content": prompt}], temperature=0.3, max_tokens=250)
        return summary.strip()
    except Exception as e:
        logger.error(f"[RESUME_ANALYSIS] Summary generation failed: {e}")
        return f"Results-driven professional with {years} years of experience specializing in {skills}."
