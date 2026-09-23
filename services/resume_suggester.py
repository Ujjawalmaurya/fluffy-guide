import json
import httpx
import asyncio
from typing import List, Dict, Optional
from loguru import logger
from app.core.config import settings
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

from app.modules.ai_chat.providers.ollama_provider import get_ollama_instance

async def improve_bullet_via_groq(bullet: str, role: Optional[str] = None) -> BulletImprovement:
    """
    Uses local Ollama model to improve a single resume bullet point into an achievement-oriented bullet.
    """
    ollama = get_ollama_instance()

    system_msg = (
        "You are a resume expert. Improve this weak resume bullet into a strong "
        "achievement-oriented bullet. Add realistic metrics if missing. Keep it under 20 words. "
        "Return ONLY valid JSON: {\"improved\": \"str\", \"reason\": \"str\"}"
    )
    user_msg = f"Original bullet: {bullet}. Role context: {role if role else 'General'}"

    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_msg}
    ]

    try:
        content = await ollama.complete_json(messages, temperature=0.3, max_tokens=150)
        return BulletImprovement(
            original=bullet,
            improved=content.get("improved", bullet),
            reason=content.get("reason", "Action-oriented refinement")
        )
    except Exception as e:
        logger.error(f"[RESUME_ANALYSIS] Ollama bullet improvement failed: {e}")
        return BulletImprovement(original=bullet, improved=bullet, reason="Could not refine bullet automatically")


async def batch_improve_bullets(bullets: List[str], role: Optional[str] = None) -> List[BulletImprovement]:
    """
    Batches bullet improvement into a single LLM call to minimise local Ollama inference latency.
    """
    if not bullets:
        return []

    ollama = get_ollama_instance()
    system_msg = (
        "You are an ATS resume optimization expert. Improve each of the given weak resume bullets "
        "into strong, action-oriented bullets with realistic metrics where possible. Keep each under 25 words. "
        "Return ONLY a JSON list of objects: [{\"original\": \"...\", \"improved\": \"...\", \"reason\": \"...\"}]"
    )
    user_msg = f"Role context: {role or 'General'}\nBullets to improve:\n" + "\n".join(f"- {b}" for b in bullets)

    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_msg}
    ]

    try:
        content = await ollama.complete_json(messages, temperature=0.3, max_tokens=600)
        items = content if isinstance(content, list) else content.get("bullets", content.get("improvements", []))
        if isinstance(items, list) and len(items) > 0:
            results = []
            for i, item in enumerate(items):
                orig = item.get("original") or (bullets[i] if i < len(bullets) else "")
                imp = item.get("improved") or orig
                reason = item.get("reason", "Action-oriented refinement")
                results.append(BulletImprovement(original=orig, improved=imp, reason=reason))
            return results
    except Exception as e:
        logger.error(f"[RESUME_ANALYSIS] Batch bullet improvement failed: {e}")

    return [
        BulletImprovement(
            original=b,
            improved=f"Delivered high-impact results by executing: {b.lstrip('- ').strip()}",
            reason="Action-verb and ownership enhancement"
        )
        for b in bullets
    ]

async def generate_summary_via_gemini(profile: StructuredProfile, target_roles: Optional[List[str]] = None) -> str:
    """
    Uses local Ollama model to generate a professional summary.
    """
    ollama = get_ollama_instance()

    name = profile.full_name or "Professional"
    skills_list = [s.name if hasattr(s, 'name') else str(s) for s in profile.skills[:5]]
    skills = ", ".join(skills_list)
    total_months = sum(exp.duration_months for exp in profile.experiences)
    years = total_months // 12

    prompt = (
        f"Generate a 3-line professional resume summary for this candidate. "
        f"Name: {name}. Experience: {years} years. Top skills: {skills}. "
        f"Target roles: {', '.join(target_roles) if target_roles else 'general'}. "
        f"Make it confident, specific, and suitable for Indian job market. Return only the 3 lines."
    )

    try:
        summary = await ollama.complete([{"role": "user", "content": prompt}], temperature=0.3, max_tokens=250)
        return summary.strip()
    except Exception as e:
        logger.error(f"[RESUME_ANALYSIS] Ollama summary generation failed: {e}")
        return f"Results-driven professional with {years} years of experience specializing in {skills}."

async def generate_suggestions(
    profile: StructuredProfile,
    quality_scores: QualityScores,
    target_roles: Optional[List[str]] = None
) -> SuggestionSet:
    """
    Generates a full set of suggestions for the resume.
    """
    logger.info("[RESUME_ANALYSIS] generating suggestions...")
    
    # Step A - Find worst bullets (rule-based)
    all_weak_bullets = []
    for exp in profile.experiences:
        for bullet in exp.responsibilities:
            all_weak_bullets.append((bullet, exp.role))
    
    all_weak_bullets.sort(key=lambda x: len(x[0]))
    worst_bullets = all_weak_bullets[:5]
    
    # Step B & C - Improve bullets in batch + Summary concurrently
    role_context = ", ".join(target_roles) if target_roles else None
    weak_bullet_texts = [b[0] for b in worst_bullets]
    
    bullet_improvements_task = batch_improve_bullets(weak_bullet_texts, role_context)
    summary_task = generate_summary_via_gemini(profile, target_roles)

    bullet_improvements, summary = await asyncio.gather(
        bullet_improvements_task,
        summary_task
    )
    
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
