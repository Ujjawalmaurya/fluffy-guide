from typing import Optional
from loguru import logger
from models.resume_analysis_models import ResumeAnalysisResult, StructuredProfile
from services.pdf_extractor import extract_resume_text
from services.resume_extractor import extract_structured_profile
from services.resume_scorer import calculate_quality_scores
from services.resume_suggester import generate_suggestions
from app.modules.ai_chat.providers.base import IStructuredProvider, ICompletionProvider

async def analyze_resume_pipeline(
    user_id: str,
    file_content: bytes,
    structured_provider: IStructuredProvider,
    completion_provider: ICompletionProvider,
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
    profile = await extract_structured_profile(raw_text, structured_provider)
    
    # 3. Rule-based Scoring
    try:
        quality_scores = calculate_quality_scores(profile, raw_text, target_role)
    except Exception as e:
        logger.error(f"[RESUME_ORCHESTRATOR] Scoring failed: {e}")
        from models.resume_analysis_models import QualityScores
        quality_scores = QualityScores()

    # 4. Suggestion Generation
    try:
        suggestions = await generate_suggestions(
            profile,
            quality_scores,
            structured_provider,
            completion_provider,
            target_role
        )
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
    
    # 6. Persist to Database (Decoupled writes)
    from app.core.database import get_supabase
    db = get_supabase()
    
    # 6.1. Upsert into resume_analysis
    try:
        # Prepare data for Supabase (convert model to dict)
        db_data = {
            "user_id": user_id,
            "structured_profile": profile.model_dump(),
            "quality_scores": quality_scores.model_dump(),
            "suggestions": suggestions.model_dump(),
            "india_flags": suggestions.india_specific_flags,
            "raw_text": raw_text,
            "overall_score": quality_scores.overall,
            "target_roles": [target_role] if target_role else [],
            "updated_at": "now()"
        }
        # Upsert returns the record if successful. on_conflict='user_id' ensures latest wins.
        db.table("resume_analysis").upsert(db_data).execute()
        logger.info(f"[RESUME_ORCHESTRATOR] Result upserted to resume_analysis for user={user_id}")
    except Exception as e:
        logger.error(f"[RESUME_ORCHESTRATOR] Resume analysis upsert failed: {str(e)}")

    # 6.2. Merge parsed skills into user_skill_profiles
    try:
        from app.modules.skill_profile import aggregator as skill_aggregator
        from app.modules.skill_profile.repository import SkillProfileRepository
        skill_repo = SkillProfileRepository(db)
        
        # Map StructuredProfile skills to aggregator format
        prof_map = {"beginner": 1, "intermediate": 2, "advanced": 3, "expert": 4}
        label_map = {"beginner": "Beginner", "intermediate": "Intermediate", "advanced": "Advanced", "expert": "Expert"}
        cleaned_skills = []
        for s in profile.skills:
            lvl = (s.level or "intermediate").lower()
            cleaned_skills.append({
                "name": s.name,
                "category": "technical",
                "proficiency_numeric": prof_map.get(lvl, 2),
                "proficiency_label": label_map.get(lvl, "Intermediate"),
                "confidence_score": 0.8
            })
        
        if cleaned_skills:
            await skill_aggregator.merge_from_resume(user_id, cleaned_skills, skill_repo)
            logger.info(f"[RESUME_ORCHESTRATOR] Skills merged into user_skill_profiles for user={user_id}. count={len(cleaned_skills)}")
    except Exception as skills_err:
        logger.error(f"[RESUME_ORCHESTRATOR] Failed to merge skills: {skills_err}")

    # 6.3. Update user_profiles table with interests and secondary skills
    try:
        profile_update = {}
        if profile.interests:
            profile_update["interests"] = profile.interests
        
        skill_names = [s.name for s in profile.skills]
        if skill_names:
            profile_update["secondary_skills"] = skill_names
            
        if profile_update:
            db.table("user_profiles").update(profile_update).eq("user_id", user_id).execute()
            logger.info(f"[RESUME_ORCHESTRATOR] Updated user_profiles for user={user_id} with: {profile_update}")
    except Exception as profile_err:
        logger.error(f"[RESUME_ORCHESTRATOR] Failed to update user_profiles: {profile_err}")

    # 6.4. Update/upsert user_preferences table with career_interests and target_roles
    try:
        prefs_update = {}
        if profile.interests:
            prefs_update["career_interests"] = profile.interests
        
        inferred_role = target_role
        if not inferred_role and hasattr(profile, "career_trajectory") and profile.career_trajectory:
            if isinstance(profile.career_trajectory, dict):
                inferred_role = profile.career_trajectory.get("summary")
            elif isinstance(profile.career_trajectory, str):
                inferred_role = profile.career_trajectory
        
        if inferred_role:
            prefs_update["target_roles"] = [inferred_role]
            
        if prefs_update:
            db.table("user_preferences").upsert({"user_id": user_id, **prefs_update}, on_conflict="user_id").execute()
            logger.info(f"[RESUME_ORCHESTRATOR] Updated user_preferences for user={user_id} with: {prefs_update}")
    except Exception as prefs_err:
        logger.error(f"[RESUME_ORCHESTRATOR] Failed to update user_preferences: {prefs_err}")
        # We still return the result so the user gets immediate feedback
    
    logger.info(f"[RESUME_ORCHESTRATOR] Pipeline complete. Score: {result.overall_score}")
    return result
