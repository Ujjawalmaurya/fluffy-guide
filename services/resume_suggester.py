import json
import httpx
import asyncio
from typing import List, Dict, Optional
from loguru import logger
from app.core.config import settings
from app.modules.ai_chat.providers.ollama_provider import get_ollama_instance
from app.core.llm_config import CAREER_CHAT, BULLET_IMPROVE
from models.resume_analysis_models import (
    StructuredProfile, QualityScores, SuggestionSet, BulletImprovement
)

# Constants for rule-based mappings
TRANSFERABLE_SKILLS_MAP = {
    "route planning": "logistics coordination",
    "cash handling": "financial accountability",
    "customer dealing": "client relationship management",
    "machine operation": "technical equipment proficiency",
    "team supervision": "team leadership",
}

WEAK_PHRASING_MAP = {
    "MS Office": "Microsoft Office Suite (Excel, Word, PowerPoint)",
    "basic computer": "Computer Proficiency",
    "internet browsing": "Digital Literacy",
    "tally": "Tally ERP 9",
    "driving": "Commercial Vehicle Operation",
}

async def improve_bullet_via_llm(bullet: str, role: Optional[str] = None) -> BulletImprovement:
    """
    Uses local Ollama to improve a single bullet point.
    """
    ollama = get_ollama_instance()
    
    system_msg = (
        "You are a resume expert. Improve this weak resume bullet into a strong "
        "achievement-oriented bullet. Add realistic metrics if missing. Keep it under 20 words. "
        "Return ONLY valid JSON: {\"improved\": \"str\", \"reason\": \"str\"}"
    )
    user_msg = f"Original bullet: {bullet}. Role context: {role if role else 'General'}"
    
    try:
        content = await ollama.complete_json([
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ], config=BULLET_IMPROVE)
        
        return BulletImprovement(
            original=bullet,
            improved=content.get("improved", bullet),
            reason=content.get("reason", "No reason provided")
        )
    except Exception as e:
        logger.error(f"[RESUME_ANALYSIS] Bullet improvement failed: {str(e)}")
        return BulletImprovement(original=bullet, improved=bullet, reason=f"Improvement failed: {str(e)}")

# Alias for backward compatibility if needed, though we should update callers
improve_bullet_via_groq = improve_bullet_via_llm

async def generate_summary_via_llm(profile: StructuredProfile, target_role: Optional[str] = None) -> str:
    """
    Uses local Ollama to generate a professional summary.
    """
    ollama = get_ollama_instance()
    
    name = profile.full_name or "Professional"
    # skills is now a list of Skill objects
    skills_list = [s.name if hasattr(s, 'name') else str(s) for s in profile.skills[:5]]
    skills = ", ".join(skills_list)
    # Calculate years of experience roughly from duration_months
    total_months = sum(exp.duration_months for exp in profile.experiences)
    years = total_months // 12
    
    prompt = (
        f"Generate a 3-line professional resume summary for this candidate. "
        f"Name: {name}. Experience: {years} years. Top skills: {skills}. "
        f"Target role: {target_role if target_role else 'general'}. "
        f"Make it confident, specific, and suitable for Indian job market. No buzzwords."
    )
    
    try:
        summary = await ollama.complete([{"role": "user", "content": prompt}], config=CAREER_CHAT)
        return summary.strip()
    except Exception as e:
        logger.error(f"[RESUME_ANALYSIS] Summary generation failed: {str(e)}")
        return "Professional seeking opportunities to leverage skills and experience in a challenging role."

# Aliases
generate_summary_via_gemini = generate_summary_via_llm

async def generate_suggestions(
    profile: StructuredProfile,
    quality_scores: QualityScores,
    target_role: Optional[str] = None
) -> SuggestionSet:
    """
    Generates a full set of suggestions for the resume.
    """
    logger.info("[RESUME_ANALYSIS] generating suggestions...")
    
    # Step A - Find worst bullets (rule-based)
    # Collect all responsibility bullets, sort by length (shortest = weakest)
    all_weak_bullets = []
    for exp in profile.experiences:
        for bullet in exp.responsibilities:
            all_weak_bullets.append((bullet, exp.role))
    
    all_weak_bullets.sort(key=lambda x: len(x[0]))
    worst_bullets = all_weak_bullets[:5]
    
    # Step B - Improve bullets via Groq
    bullet_improvements = await asyncio.gather(*[
        improve_bullet_via_groq(bullet, role) for bullet, role in worst_bullets
    ])
    
    # Step C - Summary via Gemini
    summary = await generate_summary_via_gemini(profile, target_role)
    
    # Step D - Transferable skills (rule-based)
    detected_transferable = []
    # Check skills and responsibilities
    skills_str = " ".join([s.name if hasattr(s, 'name') else str(s) for s in profile.skills])
    all_text = skills_str.lower()
    for exp in profile.experiences:
        all_text += " " + " ".join(exp.responsibilities).lower()
        all_text += " " + " ".join(exp.achievements).lower()
        
    for key, val in TRANSFERABLE_SKILLS_MAP.items():
        if key in all_text:
            detected_transferable.append(val)
            
    # Step E - Skills to reframe (rule-based)
    skills_to_reframe = {}
    for skill_obj in profile.skills:
        skill = skill_obj.name if hasattr(skill_obj, 'name') else str(skill_obj)
        for weak, strong in WEAK_PHRASING_MAP.items():
            if weak.lower() in skill.lower():
                skills_to_reframe[skill] = strong
                
    # Step F - India-specific flags
    india_flags = []
    if profile.has_photo_mentioned:
        india_flags.append("Remove photo: Modern Indian ATS/HR standards prefer no-photo resumes to avoid bias.")
    if profile.has_caste_religion_info:
        india_flags.append("Remove personal details: Caste, religion, and father's name are not required in professional resumes.")
    
    # Add generic suggestions based on missing sections
    sections_to_add = quality_scores.missing_sections
    
    return SuggestionSet(
        summary_generated=summary,
        bullet_improvements=list(bullet_improvements),
        skills_to_add=[], # Future: detect from context
        skills_to_reframe=skills_to_reframe,
        sections_to_add=sections_to_add,
        india_specific_flags=india_flags,
        transferable_skills_detected=list(set(detected_transferable))
    )
