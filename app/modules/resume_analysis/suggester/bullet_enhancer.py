"""
bullet_enhancer.py — Weak resume bullet point improvement via LLM with deterministic fallbacks.
"""
import json
from typing import List, Optional
from loguru import logger

from app.modules.resume_analysis.schemas import BulletImprovement
from app.modules.resume_analysis.prompts import (
    BULLET_IMPROVEMENT_SYSTEM_PROMPT,
    BATCH_BULLETS_SYSTEM_PROMPT,
)
from app.modules.resume_analysis.provider import get_active_provider


async def improve_bullet(bullet: str, role: Optional[str] = None) -> BulletImprovement:
    """Uses active LLM provider (Ollama / Gemini fallback) to improve a single resume bullet point."""
    provider = await get_active_provider()
    clean_bullet = bullet.lstrip("-*• ").strip()

    if provider is None:
        return BulletImprovement(
            original=bullet,
            improved=f"Spearheaded operations and delivered measurable outcomes in: {clean_bullet}",
            reason="Action-verb and ownership enhancement",
        )

    user_msg = f"Original bullet: {bullet}. Role context: {role if role else 'General'}"
    messages = [
        {"role": "system", "content": BULLET_IMPROVEMENT_SYSTEM_PROMPT},
        {"role": "user", "content": user_msg},
    ]

    try:
        if hasattr(provider, "complete_json"):
            content = await provider.complete_json(messages, temperature=0.3, max_tokens=150)
        else:
            raw = await provider.complete(messages, temperature=0.3)
            clean = raw.strip()
            if "```" in clean:
                clean = clean.split("```")[1]
                if clean.startswith("json"):
                    clean = clean[4:]
            content = json.loads(clean.strip())

        return BulletImprovement(
            original=bullet,
            improved=content.get("improved", bullet),
            reason=content.get("reason", "Action-oriented refinement"),
        )
    except Exception as e:
        logger.error(f"[RESUME_ANALYSIS] Bullet improvement failed: {e}")
        return BulletImprovement(
            original=bullet,
            improved=f"Spearheaded operations and delivered measurable outcomes in: {clean_bullet}",
            reason="Action-verb and ownership enhancement",
        )


async def batch_improve_bullets(bullets: List[str], role: Optional[str] = None) -> List[BulletImprovement]:
    """Batches bullet improvement into a single LLM call via active provider."""
    if not bullets:
        return []

    provider = await get_active_provider()
    if provider is None:
        return [
            BulletImprovement(
                original=b,
                improved=f"Delivered high-impact results by executing: {b.lstrip('-*• ').strip()}",
                reason="Action-verb and ownership enhancement",
            )
            for b in bullets
        ]

    user_msg = f"Role context: {role or 'General'}\nBullets to improve:\n" + "\n".join(f"- {b}" for b in bullets)
    messages = [
        {"role": "system", "content": BATCH_BULLETS_SYSTEM_PROMPT},
        {"role": "user", "content": user_msg},
    ]

    try:
        if hasattr(provider, "complete_json"):
            content = await provider.complete_json(messages, temperature=0.3, max_tokens=600)
        else:
            raw = await provider.complete(messages, temperature=0.3)
            clean = raw.strip()
            if "```" in clean:
                clean = clean.split("```")[1]
                if clean.startswith("json"):
                    clean = clean[4:]
            content = json.loads(clean.strip())

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
            reason="Action-verb and ownership enhancement",
        )
        for b in bullets
    ]
