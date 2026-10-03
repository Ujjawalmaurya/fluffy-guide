from uuid import UUID
from collections import defaultdict
from app.modules.skill_profile.repository import SkillProfileRepository
from app.modules.skill_profile.schemas import UserSkillProfile, SkillSummary, SkillItem

class SkillProfileService:
    def __init__(self, repo: SkillProfileRepository):
        self.repo = repo
        
    def get_profile(self, user_id: str | UUID) -> UserSkillProfile:
        db_profile = self.repo.get_by_user_id(user_id)
        if not db_profile:
            # Return empty profile if none exists
            return UserSkillProfile(
                user_id=user_id if isinstance(user_id, UUID) else UUID(user_id),
                skills=[],
                profile_version=1,
                resume_contributed=False,
                assessment_contributed=False,
                updated_at=datetime.utcnow()
            )
            
        return UserSkillProfile(**db_profile)
        
    def get_summary(self, user_id: str | UUID) -> SkillSummary:
        profile = self.get_profile(user_id)
        skills = profile.skills
        
        by_category = defaultdict(list)
        source_breakdown = {"resume_only": 0, "assessment_only": 0, "both": 0}
        
        for skill in skills:
            by_category[skill.category].append(skill)
            
            src = skill.source
            if src == "resume":
                source_breakdown["resume_only"] += 1
            elif src == "assessment":
                source_breakdown["assessment_only"] += 1
            elif src == "both":
                source_breakdown["both"] += 1
                
        # Top 5 sorted by proficiency_numeric desc
        top_5 = sorted(skills, key=lambda x: x.proficiency_numeric, reverse=True)[:5]
        
        return SkillSummary(
            total_skills=len(skills),
            by_category=dict(by_category),
            top_5=top_5,
            source_breakdown=source_breakdown
        )
