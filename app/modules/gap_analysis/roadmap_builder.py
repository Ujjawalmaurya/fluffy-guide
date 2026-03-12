# [GAP_ANALYSIS] Builds personalized learning roadmap using Gemini.
# Always picks resources from DB — never lets Gemini invent them.

import json
from app.modules.learning_resources import repository as res_repo
from app.core.logger import get_logger

logger = get_logger("GAP_ANALYSIS")

ROADMAP_PROMPT = """
You are a career development expert for India's workforce.
Build a practical week-by-week learning roadmap.
Return ONLY valid JSON. No markdown. No preamble. No explanation.

User profile:
- Name: {name}
- User type: {user_type}
- State: {state}
- Career interests: {interests}

Top skill gaps to address (in priority order):
{top_gaps}

Available learning resources (USE ONLY THESE — never invent):
{resources_json}

Rules:
- Plan 8 to 12 weeks total
- Max 2-3 hours per day commitment
- Blue-collar workers: prefer vocational, hands-on resources
- Youth: include one soft skill week alongside technical weeks
- Each week focuses on ONE skill only
- Milestones must be concrete and personally verifiable
- motivational_note must be specific to this person, not generic

Return ONLY this JSON:
{{
  "total_weeks": 10,
  "weekly_commitment_hours": 2,
  "roadmap": [
    {{
      "week": 1,
      "focus_skill": "skill name",
      "goal": "what they can do by end of this week",
      "action": "specific daily action in plain simple language",
      "resource_id": "uuid from provided resources or null",
      "resource_name": "name from provided list or null",
      "resource_url": "url from provided list or null",
      "milestone": "I will know I succeeded when I can..."
    }}
  ],
  "motivational_note": "one specific encouraging sentence"
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
    gemini_provider
) -> tuple[dict, list]:
    """
    Fetches matching resources for top 5 gaps, then calls
    Gemini to generate a personalized week-by-week roadmap.
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

    prompt = ROADMAP_PROMPT.format(
        name=user_profile_data.get("full_name", "there"),
        user_type=user_profile_data.get("user_type", "individual"),
        state=user_profile_data.get("state", "India"),
        interests=", ".join(
            user_profile_data.get("career_interests") or []
        ),
        top_gaps=json.dumps(
            [g["skill_name"] for g in top_gaps]
        ),
        resources_json=json.dumps(all_resources, default=str)
    )

    response = await gemini_provider.complete(
        [{"role": "user", "content": prompt}]
    )

    clean = _strip_fences(response)
    try:
        roadmap_data = json.loads(clean)
    except json.JSONDecodeError:
        logger.error(f"[GAP_ANALYSIS] Failed to parse roadmap JSON: {clean[:200]}...")
        roadmap_data = {"roadmap": [], "motivational_note": "Keep learning!"}

    logger.info(
        f"[GAP_ANALYSIS] Roadmap built for user={user_id}. "
        f"weeks={roadmap_data.get('total_weeks')}"
    )

    return roadmap_data, enriched_gaps
