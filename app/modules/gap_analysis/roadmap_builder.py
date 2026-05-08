# [GAP_ANALYSIS] Builds personalized learning roadmap using Gemini.
# Always picks resources from DB — never lets Gemini invent them.

import json
from app.modules.learning_resources import repository as res_repo
from app.core.logger import get_logger

logger = get_logger("GAP_ANALYSIS")

from app.core.llm_config import CONCISENESS_INSTRUCTION

ROADMAP_SYSTEM_PROMPT = f"""ROLE: You are an elite career development expert for India's workforce, specializing in SkillBridge AI.

TASK: Build a practical week-by-week learning roadmap.
JSON ONLY. No prose. No markdown. No explanation.

RULES:
- Plan 8 to 12 weeks total.
- Max 2-3 hours per day commitment.
- Blue-collar workers: prefer vocational, hands-on resources.
- Youth: include one soft skill week alongside technical weeks.
- Each week focuses on ONE skill only.
- Milestones must be concrete and personally verifiable.
- motivational_note must be specific to this person, not generic.
- USE ONLY the provided resources. Never invent URLs or IDs.

{CONCISENESS_INSTRUCTION}
"""

ROADMAP_USER_PROMPT = """USER PROFILE:
- Name: {name}
- Type: {user_type}
- State: {state}
- Interests: {interests}

TOP SKILL GAPS:
{top_gaps}

AVAILABLE RESOURCES:
{resources_json}

Return ONLY this JSON structure:
{{
  "total_weeks": 10,
  "weekly_commitment_hours": 2,
  "roadmap": [
    {{
      "week": 1,
      "focus_skill": "...",
      "goal": "...",
      "action": "...",
      "resource_id": "...",
      "resource_name": "...",
      "resource_url": "...",
      "milestone": "..."
    }}
  ],
  "motivational_note": "..."
}}
"""

def _strip_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = lines[1:] if lines[0].startswith("```") else lines
        lines = lines[:-1] if lines and lines[-1].strip() == "```" else lines
        text = "\n".join(lines)
    return text.strip()

async def build_roadmap(
    user_id: str,
    gaps: list,
    user_profile_data: dict,
    llm_provider
) -> tuple[dict, list]:
    """
    Fetches matching resources for top 5 gaps, then calls
    LLM to generate a personalized week-by-week roadmap.
    Returns (roadmap_data, enriched_gaps_with_resource_ids).
    """
    top_gaps = gaps[:5]

    # Fetch matching resources from DB for each gap
    enriched_gaps = []
    all_resources = []
    seen_ids = set()

    for gap in top_gaps:
        resources = await res_repo.find_by_skill_tag(
            gap["skill_name"], limit=3
        )
        gap["recommended_resources"] = [r["id"] for r in resources]
        enriched_gaps.append(gap)
        for r in resources:
            if r["id"] not in seen_ids:
                all_resources.append(r)
                seen_ids.add(r["id"])

    if not all_resources:
        logger.warning(
            f"[GAP_ANALYSIS] No matching resources found for "
            f"user={user_id}. Roadmap will have no resource links."
        )

    user_prompt = ROADMAP_USER_PROMPT.format(
        name=user_profile_data.get("full_name", "there"),
        user_type=user_profile_data.get("user_type", "individual"),
        state=user_profile_data.get("state", "India"),
        interests=", ".join(
            str(i.get("label") if isinstance(i, dict) else i)
            for i in (user_profile_data.get("career_interests") or [])
        ),
        top_gaps=json.dumps(
            [g["skill_name"] for g in top_gaps]
        ),
        resources_json=json.dumps(all_resources, default=str)
    )

    from app.core.llm_config import LLM_TASKS
    from app.schemas.internal.llm_outputs import RoadmapLLMOutput

    roadmap_raw = await llm_provider.complete_json(
        messages=[
            {"role": "system", "content": ROADMAP_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        config=LLM_TASKS["roadmap"]
    )

    try:
        if not roadmap_raw:
            raise ValueError("Empty response from LLM")
        
        # Validate using Pydantic model
        roadmap_model = RoadmapLLMOutput.model_validate(roadmap_raw)
        roadmap_data = roadmap_model.model_dump()
        
    except Exception as e:
        logger.error(f"[GAP_ANALYSIS] Failed to validate roadmap JSON: {e}")
        # Fallback to safe defaults
        roadmap_data = RoadmapLLMOutput().model_dump()

    logger.info(
        f"[GAP_ANALYSIS] Roadmap built for user={user_id}. "
        f"weeks={roadmap_data.get('total_weeks')}"
    )

    return roadmap_data, enriched_gaps
