"""
related_skills.py — POST /api/skills/related
Uses Groq Llama3 to suggest related/adjacent skills for a given seed skill.
Intended for the onboarding bubble-grid animation.
"""
import json
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from groq import Groq

router = APIRouter()

_client: Groq | None = None

def _get_client() -> Groq:
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY", "")
        if not api_key:
            raise HTTPException(status_code=503, detail="GROQ_API_KEY not configured")
        _client = Groq(api_key=api_key)
    return _client


class RelatedSkillsRequest(BaseModel):
    seed_skill: str
    career_domain: str = "general"
    limit: int = 8


class RelatedSkillsResponse(BaseModel):
    seeds: list[str]
    related: list[str]


SYSTEM_PROMPT = """You are a career skills expert for the Indian job market.
Given a seed skill and career domain, return a JSON object with:
- "seeds": list of 2-3 core/parent skills (very broad categories the seed belongs to)
- "related": list of {limit} adjacent/complementary skills that someone with this skill often needs

Rules:
- Keep all skill names SHORT (1-3 words max)
- Focus on practical, in-demand skills for India
- JSON only, no markdown, no explanation
- Example output: {{"seeds": ["Sales"], "related": ["CRM Software", "Lead Generation", "Cold Calling", "Negotiation", "Target Achievement", "B2B Sales", "Tele-sales", "Product Demo"]}}
"""


@router.post("/api/skills/related", response_model=RelatedSkillsResponse)
async def get_related_skills(req: RelatedSkillsRequest):
    client = _get_client()
    
    prompt = (
        f"Seed skill: {req.seed_skill}\n"
        f"Career domain: {req.career_domain}\n"
        f"Return {req.limit} related skills."
    )
    
    try:
        resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT.replace("{limit}", str(req.limit))},
                {"role": "user", "content": prompt},
            ],
            max_tokens=256,
            temperature=0.7,
        )
        raw = resp.choices[0].message.content.strip()
        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        data = json.loads(raw)
        return RelatedSkillsResponse(
            seeds=data.get("seeds", [req.seed_skill]),
            related=data.get("related", []),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Skill suggestion failed: {str(e)}")
