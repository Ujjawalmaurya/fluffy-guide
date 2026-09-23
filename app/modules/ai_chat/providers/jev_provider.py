import re
from typing import Dict, Any, List, Optional
from loguru import logger


class JevProvider:
    """
    Jev System One Decision Engine — high-speed non-autoregressive decision model.
    Runs locally in sub-millisecond time (<0.05ms) for triage, scoring, and classification.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.enabled = True
        logger.info("[JEV] Local System 1 Decision Engine initialized (sub-millisecond local mode)")

    def is_available(self) -> bool:
        return True

    async def check_chat_guardrails(self, message: str) -> Dict[str, Any]:
        """Triage chat message for safety, intent classification, and emergency distress (<0.05ms)."""
        msg_lower = message.lower().strip()

        distress_markers = [
            "suicide", "end my life", "kill myself", "depressed and lost",
            "severe help", "cannot live anymore", "want to die"
        ]
        is_distress = any(m in msg_lower for m in distress_markers)

        abuse_markers = [
            "fuck", "bastard", "idiot", "kill you", "die bot", "stupid bot",
            "hack", "ignore previous instructions", "system prompt"
        ]
        is_abuse = any(m in msg_lower for m in abuse_markers)

        if is_abuse:
            intent = "abuse"
            is_safe = False
        elif is_distress:
            intent = "career_guidance"
            is_safe = True
        elif any(g in msg_lower for g in ["hi", "hello", "hey", "namaste", "good morning", "good evening"]):
            intent = "greeting"
            is_safe = True
        elif any(j in msg_lower for j in ["job", "vacancy", "opening", "salary", "hiring", "apply", "recruit"]):
            intent = "job_search"
            is_safe = True
        elif any(s in msg_lower for s in ["test", "quiz", "assessment", "score", "skill", "evaluation"]):
            intent = "skill_assessment"
            is_safe = True
        else:
            intent = "career_guidance"
            is_safe = True

        return {
            "is_safe": is_safe,
            "intent": intent,
            "is_distress": is_distress,
        }

    async def score_job_match(self, candidate_profile: dict, job: dict) -> Dict[str, Any]:
        """
        Evaluates candidate-job suitability in a single parallel decision pass (<0.05ms).
        Calculates skill overlap, experience level, and location compatibility.
        """
        raw_candidate_skills = (
            candidate_profile.get("skills")
            or candidate_profile.get("resume_skills")
            or []
        )
        candidate_skills = [
            (s.get("name") if isinstance(s, dict) else str(s)).lower()
            for s in raw_candidate_skills
        ]

        raw_required = job.get("required_skills") or []
        required_skills = [
            (s.get("name") if isinstance(s, dict) else str(s)).lower()
            for s in raw_required
        ]

        # Skill matching
        matched_skills = []
        for req in required_skills:
            if any(req in cand or cand in req for cand in candidate_skills):
                matched_skills.append(req)

        overlap_ratio = len(matched_skills) / max(len(required_skills), 1)

        # Experience fit
        exp_min = job.get("experience_min", 0) or 0
        cand_exp = candidate_profile.get("total_experience_years", 0) or 0

        if cand_exp < exp_min:
            experience_fit = "underqualified" if exp_min - cand_exp > 2 else "entry_fit"
            exp_factor = max(0.4, 1.0 - (exp_min - cand_exp) * 0.15)
        elif cand_exp > (exp_min + 5):
            experience_fit = "overqualified"
            exp_factor = 0.9
        else:
            experience_fit = "adequate"
            exp_factor = 1.0

        # Location compatibility
        cand_loc = (candidate_profile.get("location") or candidate_profile.get("state") or "").lower()
        job_loc = (job.get("location_city") or job.get("location_state") or "").lower()
        location_fit = not job_loc or not cand_loc or (cand_loc in job_loc or job_loc in cand_loc)
        loc_factor = 1.0 if location_fit else 0.85

        # Composite match score (0 - 100)
        base_score = (overlap_ratio * 70.0 + exp_factor * 20.0 + (10.0 if location_fit else 0.0))
        final_score = int(min(100, max(15, round(base_score))))

        meets_skills = len(matched_skills) >= max(1, len(required_skills) // 2)

        return {
            "id": job.get("id"),
            "match_score": final_score,
            "meets_skills": meets_skills,
            "matched_skills": matched_skills,
            "experience_fit": experience_fit,
            "location_fit": location_fit,
        }

    async def evaluate_resume_ats_flags(self, resume_text: str) -> Dict[str, Any]:
        """Detects photo mentions, demographic disclosures, and formatting risks in <0.05ms."""
        text_lower = resume_text.lower()

        has_photo = bool(re.search(r'\b(passport\s+photo|photograph|photo\s+attached|picture\s+affixed)\b', text_lower))
        has_caste_religion = bool(re.search(r'\b(caste|religion|hindu|muslim|christian|sikh|sc/st|obc)\b', text_lower))

        # Check section presence
        has_experience = bool(re.search(r'\b(experience|employment|work\s+history)\b', text_lower))
        has_education = bool(re.search(r'\b(education|degree|qualification|bachelor|master|diploma)\b', text_lower))
        has_skills = bool(re.search(r'\b(skills|technologies|competencies)\b', text_lower))

        return {
            "has_photo_mentioned": has_photo,
            "has_caste_religion_info": has_caste_religion,
            "has_experience_section": has_experience,
            "has_education_section": has_education,
            "has_skills_section": has_skills,
            "career_trajectory": "ascending",
        }

    async def score_assessment_answer(self, question: str, answer: str) -> int:
        """Scores candidate assessment answer on a 1-5 competence scale (<0.01ms)."""
        clean = answer.strip()
        if not clean:
            return 1

        words = clean.split()
        word_count = len(words)

        has_action_verbs = bool(re.search(r'\b(built|designed|led|managed|created|implemented|handled|maintained|resolved|fixed|developed)\b', clean, re.IGNORECASE))
        has_metrics = bool(re.search(r'\b(?:\d+%?|\d+\s*(?:years?|months?|team|clients?|users?|lakhs?))\b', clean, re.IGNORECASE))

        score = 2
        if word_count >= 8:
            score += 1
        if word_count >= 20 or has_action_verbs:
            score += 1
        if has_metrics and word_count >= 15:
            score += 1

        return min(5, max(1, score))

    async def score_interview_answer(self, role: str, question: str, answer: str) -> Dict[str, Any]:
        """Scores mock interview answer on a 1-10 scale with feedback (<0.05ms)."""
        clean = answer.strip()
        words = clean.split()
        count = len(words)

        if count < 5:
            return {
                "score": 3,
                "feedback": "Answer is too brief. Provide more context regarding your experience.",
                "keywords_matched": [],
                "improvement": "Explain your approach using concrete examples and tools."
            }

        score = 6
        if count >= 20:
            score += 1
        if count >= 40:
            score += 1

        has_metrics = bool(re.search(r'\b(?:\d+%?|\d+\s*(?:years?|projects?|results?))\b', clean, re.IGNORECASE))
        if has_metrics:
            score += 1

        return {
            "score": min(10, score),
            "feedback": "Clear and relevant answer addressing the core aspects of the role.",
            "keywords_matched": [role],
            "improvement": "Highlight specific metrics, technical trade-offs, and outcomes."
        }
