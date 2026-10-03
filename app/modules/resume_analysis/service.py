"""
service.py — High-level resume analysis orchestrator service.
Executes multi-stage pipeline: PDF extraction -> Deterministic + LLM extraction -> Scoring -> Suggestions -> Persistence.
"""
from datetime import datetime
from typing import List, Optional
from loguru import logger

from app.modules.resume_analysis.schemas import (
    QualityScores,
    ResumeAnalysisResult,
    StructuredProfile,
    SuggestionSet,
)
from app.modules.resume_analysis.pdf import extract_resume_text
from app.modules.resume_analysis.llm_extractor import extract_structured_profile
from app.modules.resume_analysis.scorer import calculate_quality_scores
from app.modules.resume_analysis.suggester import generate_suggestions
from app.modules.resume_analysis.repository import ResumeAnalysisRepository


class ResumeAnalysisService:
    def __init__(self, repo: Optional[ResumeAnalysisRepository] = None):
        self.repo = repo or ResumeAnalysisRepository()

    async def analyze(
        self,
        user_id: str,
        file_content: bytes,
        target_roles: Optional[List[str]] = None,
    ) -> ResumeAnalysisResult:
        """
        Complete production-grade analyzer pipeline.
        Fail-safe operation: always returns valid result even if AI or DB partially fails.
        """
        logger.info(f"[RESUME_SERVICE] Starting analysis for user={user_id}")

        # 1. Extraction (Robust PyMuPDF with text fallback)
        try:
            raw_text = extract_resume_text(file_content)
        except Exception as e:
            logger.error(f"[RESUME_SERVICE] PDF Extraction failed: {e}")
            raw_text = ""

        # 2. AI Structured Extraction (Deterministic Preflight + LLM Synthesis)
        profile = await extract_structured_profile(raw_text)

        # 2b. Merge Manual and Inferred Target Roles
        effective_roles = list(target_roles or [])
        if profile.inferred_target_roles:
            existing_roles_lower = {r.lower() for r in effective_roles}
            for role in profile.inferred_target_roles:
                if role.lower() not in existing_roles_lower:
                    effective_roles.append(role)

        # 3. Rule-based Scoring
        try:
            quality_scores = calculate_quality_scores(profile, raw_text, effective_roles)
        except Exception as e:
            logger.error(f"[RESUME_SERVICE] Scoring failed: {e}")
            quality_scores = QualityScores()

        # 4. Suggestion Generation
        try:
            suggestions = await generate_suggestions(profile, quality_scores, effective_roles)
        except Exception as e:
            logger.error(f"[RESUME_SERVICE] Suggestion generation failed: {e}")
            suggestions = SuggestionSet()

        # 5. Build Final Result
        now_iso = datetime.utcnow().isoformat()
        result = ResumeAnalysisResult(
            user_id=user_id,
            structured_profile=profile,
            quality_scores=quality_scores,
            suggestions=suggestions,
            overall_score=quality_scores.overall,
            target_roles=effective_roles,
            india_flags=suggestions.india_specific_flags,
            raw_text=raw_text,
            created_at=now_iso,
            updated_at=now_iso,
        )

        # 6. Database Persistence
        self.repo.upsert_analysis(user_id, result, effective_roles)

        # 7. Auto-sync skills to user_skill_profiles
        await self.repo.sync_skills_to_profile(user_id, profile)

        logger.info(f"[RESUME_SERVICE] Pipeline complete. Score: {result.overall_score}")
        return result
