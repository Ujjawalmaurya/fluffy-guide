from typing import Optional
from loguru import logger
from models.resume_analysis_models import ResumeAnalysisResult, StructuredProfile
from services.pdf_extractor import extract_resume_text
from services.resume_extractor import extract_structured_profile
from services.resume_scorer import calculate_quality_scores
from services.resume_suggester import generate_suggestions
# from app.core.database import supabase # If we were saving, but user didn't ask yet

async def analyze_resume_pipeline(
    user_id: str,
    file_content: bytes,
    target_role: Optional[str] = None
) -> ResumeAnalysisResult:
    """
    Complete production-grade analyzer pipeline.
    Ensures fail-safe operation: always returns a result even if AI partially fails.
    """
    logger.info(f"[RESUME_ORCHESTRATOR] Starting analysis for user={user_id}")
    
    # 1. Extraction (Robust)
    try:
        raw_text = extract_resume_text(file_content)
    except Exception as e:
        logger.error(f"[RESUME_ORCHESTRATOR] PDF Extraction failed: {e}")
        raw_text = ""

    # 2. AI Structured Extraction (Fail-safe)
    # The extractor now returns a default StructuredProfile() on failure
    profile = await extract_structured_profile(raw_text)
    
    # 3. Rule-based Scoring
    try:
        quality_scores = calculate_quality_scores(profile, raw_text, target_role)
    except Exception as e:
        logger.error(f"[RESUME_ORCHESTRATOR] Scoring failed: {e}")
        from models.resume_analysis_models import QualityScores
        quality_scores = QualityScores()

    # 4. Suggestion Generation
    try:
        suggestions = await generate_suggestions(profile, quality_scores, target_role)
    except Exception as e:
        logger.error(f"[RESUME_ORCHESTRATOR] Suggestion generation failed: {e}")
        from models.resume_analysis_models import SuggestionSet
        suggestions = SuggestionSet()

    # 5. Build Final Result
    result = ResumeAnalysisResult(
        user_id=user_id,
        structured_profile=profile,
        quality_scores=quality_scores,
        suggestions=suggestions,
        overall_score=quality_scores.overall,
        target_role=target_role,
        india_flags=suggestions.india_specific_flags,
        raw_text=raw_text
    )
    
    # 6. Persist to Database (Upsert: one analysis per user)
    try:
        from app.core.database import get_supabase
        db = get_supabase()
        
        # Prepare data for Supabase (convert model to dict)
        db_data = {
            "user_id": user_id,
            "structured_profile": profile.model_dump(),
            "quality_scores": quality_scores.model_dump(),
            "suggestions": suggestions.model_dump(),
            "india_flags": suggestions.india_specific_flags,
            "raw_text": raw_text,
            "overall_score": quality_scores.overall,
            "target_role": target_role,
            "updated_at": "now()"
        }
        
        # Upsert returns the record if successful. on_conflict='user_id' ensures latest wins.
        db.table("resume_analysis").upsert(db_data).execute()
        logger.info(f"[RESUME_ORCHESTRATOR] Result upserted to database for user={user_id}")
        
    except Exception as e:
        logger.error(f"[RESUME_ORCHESTRATOR] Database persistence failed: {str(e)}")
        # We still return the result so the user gets immediate feedback
    
    logger.info(f"[RESUME_ORCHESTRATOR] Pipeline complete. Score: {result.overall_score}")
    return result
