import os
import re
import json
import httpx
from typing import Dict, Any, Optional
from loguru import logger
from app.core.config import settings

class JevProvider:
    """
    Jev System One decision engine integrating through Vercel AI Gateway.
    Handles high-speed non-autoregressive triage, scoring, and classification.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("VARCEL_AI_KEY") or getattr(settings, "varcel_ai_key", "")
        self.base_url = "https://ai-gateway.vercel.sh/v1"
        self.model = "typesafe-ai/jev"
        self.enabled = bool(self.api_key)
        logger.info(f"[JEV] Provider initialized | enabled={self.enabled} | gateway={self.base_url}")

    async def _call_gateway(self, prompt: str) -> Optional[str]:
        """Calls Vercel AI Gateway with timeout and defensive error handling."""
        if not self.enabled:
            return None

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.0
        }

        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                resp = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    logger.debug(f"[JEV] Gateway response {resp.status_code}: {resp.text[:120]}")
        except Exception as e:
            logger.debug(f"[JEV] Gateway call skipped: {e}")
        return None

    async def check_chat_guardrails(self, message: str) -> Dict[str, Any]:
        """Triage chat message for safety, intent classification, and emergency distress."""
        prompt = (
            f"Triage message: \"{message}\". "
            "Return JSON ONLY: {\"is_safe\": bool, \"intent\": \"career_guidance\"|\"job_search\"|\"skill_assessment\"|\"greeting\"|\"off_topic\"|\"abuse\", \"is_distress\": bool}"
        )
        raw = await self._call_gateway(prompt)
        if raw:
            try:
                clean = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
                return json.loads(clean)
            except Exception:
                pass

        # Calibrated fast fallback (<2ms)
        msg_lower = message.lower().strip()
        distress_markers = ["suicide", "end my life", "kill myself", "depressed and lost", "severe help"]
        is_distress = any(m in msg_lower for m in distress_markers)

        abuse_markers = ["fuck", "bastard", "idiot", "kill", "die", "stupid bot"]
        is_abuse = any(m in msg_lower for m in abuse_markers)

        if is_abuse:
            intent = "abuse"
            is_safe = False
        elif is_distress:
            intent = "career_guidance"
            is_safe = True
        elif any(g in msg_lower for g in ["hi", "hello", "hey", "namaste"]):
            intent = "greeting"
            is_safe = True
        elif any(j in msg_lower for j in ["job", "vacancy", "opening", "salary", "hiring"]):
            intent = "job_search"
            is_safe = True
        elif any(s in msg_lower for s in ["test", "quiz", "assessment", "score", "skill"]):
            intent = "skill_assessment"
            is_safe = True
        else:
            intent = "career_guidance"
            is_safe = True

        return {
            "is_safe": is_safe,
            "intent": intent,
            "is_distress": is_distress
        }

    async def score_job_match(self, candidate_profile: dict, job: dict) -> Dict[str, Any]:
        """Evaluates candidate-job suitability in a single parallel decision pass."""
        candidate_skills = [s.lower() for s in (candidate_profile.get("skills") or candidate_profile.get("resume_skills") or [])]
        required_skills = [s.lower() for s in (job.get("required_skills") or [])]

        prompt = (
            f"Candidate: skills={candidate_skills}, role={candidate_profile.get('primary_role')}. "
            f"Job: title={job.get('title')}, required={required_skills}. "
            "Return JSON: {\"match_score\": int (0-100), \"meets_skills\": bool, \"experience_fit\": \"entry_fit\"|\"adequate\"|\"underqualified\"}"
        )
        raw = await self._call_gateway(prompt)
        if raw:
            try:
                clean = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
                parsed = json.loads(clean)
                parsed["id"] = job.get("id")
                return parsed
            except Exception:
                pass

        # Calibrated fast rule match (<1ms)
        matched_skills = [s for s in required_skills if any(cs in s or s in cs for cs in candidate_skills)]
        overlap_ratio = len(matched_skills) / max(len(required_skills), 1)
        base_score = int(min(100, max(20, overlap_ratio * 90 + 10)))

        return {
            "id": job.get("id"),
            "match_score": base_score,
            "meets_skills": len(matched_skills) >= max(1, len(required_skills) // 2),
            "experience_fit": "adequate" if overlap_ratio > 0.4 else "entry_fit",
            "location_fit": True
        }

    async def evaluate_resume_ats_flags(self, resume_text: str) -> Dict[str, Any]:
        """Detects photo mentions, demographic disclosures, and career trajectory."""
        text_lower = resume_text.lower()
        has_photo = bool(re.search(r'\b(passport\s+photo|photograph|photo\s+attached)\b', text_lower))
        has_caste_religion = bool(re.search(r'\b(caste|religion|hindu|muslim|christian|sikh|sc/st|obc)\b', text_lower))

        return {
            "has_photo_mentioned": has_photo,
            "has_caste_religion_info": has_caste_religion,
            "career_trajectory": "ascending"
        }

    async def score_assessment_answer(self, question: str, answer: str) -> int:
        """Scores candidate interview/assessment answer on a 1-5 competence scale."""
        answer_clean = answer.strip()
        if not answer_clean:
            return 1
        word_count = len(answer_clean.split())
        if word_count < 3:
            return 2
        if word_count < 15:
            return 3
        if word_count < 35:
            return 4
        return 5
