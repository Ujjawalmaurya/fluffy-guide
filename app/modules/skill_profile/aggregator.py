from uuid import UUID
from loguru import logger
from datetime import datetime, timezone
from app.modules.skill_profile.repository import SkillProfileRepository

async def merge_from_resume(user_id: str | UUID, resume_skills: list[dict], repo: SkillProfileRepository):
    """
    Merges Gemini-extracted resume skills into user_skill_profiles.
    Resolution rule: if skill exists from assessment, keep HIGHER proficiency.
    When both sources agree, set source='both'.
    """
    existing_profile = repo.get_by_user_id(user_id) or {}
    existing_skills_list = existing_profile.get("skills", [])
    
    # Build dict keyed by lowercase skill name
    existing_skills = {s.get("skill_name", "").strip().lower(): s for s in existing_skills_list}
    
    n_added = 0
    n_updated = 0
    
    for inc_skill in resume_skills:
        skill_name = inc_skill.get("name", inc_skill.get("skill_name", ""))
        skill_key = skill_name.strip().lower()
        if not skill_key:
            continue
            
        inc_prof = int(inc_skill.get("proficiency_numeric", 1))
        inc_conf = float(inc_skill.get("confidence", inc_skill.get("confidence_score", 0.0)))
        
        if skill_key not in existing_skills:
            # Add new skill
            new_skill = {
                "skill_name": skill_name,
                "category": inc_skill.get("category", "technical"),
                "proficiency_numeric": inc_prof,
                "proficiency_label": inc_skill.get("proficiency_label", "Beginner"),
                "source": "resume",
                "confidence_score": inc_conf,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            existing_skills[skill_key] = new_skill
            n_added += 1
        else:
            ex_skill = existing_skills[skill_key]
            
            if ex_skill.get("source") == "assessment":
                # Keep higher proficiency
                ex_prof = int(ex_skill.get("proficiency_numeric", 1))
                new_prof = max(ex_prof, inc_prof)
                ex_skill["proficiency_numeric"] = new_prof
                ex_skill["source"] = "both"
                ex_skill["confidence_score"] = max(ex_skill.get("confidence_score", 0.0), inc_conf)
                ex_skill["last_updated"] = datetime.now(timezone.utc).isoformat()
                n_updated += 1
                
            elif ex_skill.get("source") == "resume":
                # Update if incoming confidence is higher
                if inc_conf > ex_skill.get("confidence_score", 0.0):
                    ex_skill["proficiency_numeric"] = inc_prof
                    ex_skill["proficiency_label"] = inc_skill.get("proficiency_label", "Beginner")
                    ex_skill["confidence_score"] = inc_conf
                    ex_skill["last_updated"] = datetime.now(timezone.utc).isoformat()
                    n_updated += 1
                    
            elif ex_skill.get("source") == "both":
                # Check confidence for both
                if inc_conf > ex_skill.get("confidence_score", 0.0):
                    ex_prof = int(ex_skill.get("proficiency_numeric", 1))
                    ex_skill["proficiency_numeric"] = max(ex_prof, inc_prof)
                    ex_skill["confidence_score"] = inc_conf
                    ex_skill["last_updated"] = datetime.now(timezone.utc).isoformat()
                    n_updated += 1

    merged_skills = list(existing_skills.values())
    
    resume_contributed = True
    assessment_contributed = existing_profile.get("assessment_contributed", False)
    
    repo.upsert(user_id, merged_skills, resume_contributed, assessment_contributed)
    repo.increment_version(user_id)
    
    logger.info(f"[SKILL_PROFILE] [INFO] Resume merge complete for user={user_id}. Added={n_added}, Updated={n_updated}. Total={len(merged_skills)} skills.")

async def merge_from_assessment(user_id: str | UUID, assessment_skills: list[dict], repo: SkillProfileRepository):
    """
    Merges skills extracted from completed assessment.
    Assessment proficiency is more reliable than resume inference.
    So when conflict: assessment wins for proficiency_numeric.
    """
    existing_profile = repo.get_by_user_id(user_id) or {}
    existing_skills_list = existing_profile.get("skills", [])
    
    existing_skills = {s.get("skill_name", "").strip().lower(): s for s in existing_skills_list}
    
    for inc_skill in assessment_skills:
        skill_name = inc_skill.get("skill_name", inc_skill.get("name", ""))
        skill_key = skill_name.strip().lower()
        if not skill_key:
            continue
            
        inc_prof = int(inc_skill.get("proficiency_numeric", 1))
        inc_conf = float(inc_skill.get("confidence", inc_skill.get("confidence_score", 0.0)))
        
        if skill_key not in existing_skills:
            # Add new skill
            new_skill = {
                "skill_name": skill_name,
                "category": inc_skill.get("category", "technical"),
                "proficiency_numeric": inc_prof,
                "proficiency_label": inc_skill.get("proficiency_label", "Beginner"),
                "source": "assessment",
                "confidence_score": inc_conf,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            existing_skills[skill_key] = new_skill
        else:
            ex_skill = existing_skills[skill_key]
            
            if ex_skill.get("source") == "resume":
                # Assessment wins for proficiency numeric
                ex_skill["proficiency_numeric"] = inc_prof
                ex_skill["proficiency_label"] = inc_skill.get("proficiency_label", "Beginner")
                ex_skill["source"] = "both"
                ex_skill["confidence_score"] = max(ex_skill.get("confidence_score", 0.0), inc_conf)
                ex_skill["last_updated"] = datetime.now(timezone.utc).isoformat()
                
            elif ex_skill.get("source") == "assessment":
                # Update if incoming confidence is higher
                if inc_conf > ex_skill.get("confidence_score", 0.0):
                    ex_skill["proficiency_numeric"] = inc_prof
                    ex_skill["proficiency_label"] = inc_skill.get("proficiency_label", "Beginner")
                    ex_skill["confidence_score"] = inc_conf
                    ex_skill["last_updated"] = datetime.now(timezone.utc).isoformat()
                    
            elif ex_skill.get("source") == "both":
                # Assessment wins, so ensure proficiency updates
                ex_skill["proficiency_numeric"] = inc_prof
                ex_skill["proficiency_label"] = inc_skill.get("proficiency_label", "Beginner")
                ex_skill["confidence_score"] = max(ex_skill.get("confidence_score", 0.0), inc_conf)
                ex_skill["last_updated"] = datetime.now(timezone.utc).isoformat()
                
    merged_skills = list(existing_skills.values())
    
    resume_contributed = existing_profile.get("resume_contributed", False)
    assessment_contributed = True
    
    repo.upsert(user_id, merged_skills, resume_contributed, assessment_contributed)
    repo.increment_version(user_id)
    
    logger.info(f"[SKILL_PROFILE] [INFO] Assessment merge complete for user={user_id}. Total skills={len(merged_skills)}")
