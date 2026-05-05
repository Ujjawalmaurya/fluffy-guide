from typing import Optional
from .repository import GapAnalysisRepository, GapAnalysisReport
from .domain import GapAnalysisDomain, UserSkillProfile, SkillEntry, GapEntry
from .ai_pipeline import GapAnalysisAIPipeline
from .exceptions import GapAnalysisException

class GapAnalysisService:
    def __init__(self, repo: GapAnalysisRepository, ai: GapAnalysisAIPipeline, domain: GapAnalysisDomain):
        self.repo = repo
        self.ai = ai
        self.domain = domain

    async def get_or_compute_report(self, user_id: str, target_roles: list[str], state: str) -> GapAnalysisReport:
        # 1. Load skill profile from repo (Mocking profile fetch for now)
        # In real app: profile_data = await self.repo.get_user_profile(user_id)
        # For this implementation, we assume it's passed or fetched.
        # Let's assume we have a way to get it.
        profile_data = await self.repo.get_cached_report(user_id) # Placeholder for profile fetch
        
        # Stubbing a skill profile for orchestration flow if none exists
        if not profile_data:
            skill_profile = UserSkillProfile(skills=[SkillEntry(skill_name="Python", proficiency=2)])
        else:
            # Convert repo data to domain model
            skill_profile = UserSkillProfile(skills=[SkillEntry(**s) for s in profile_data.report_data.get('skills', [])])

        # 2. Compute hash via domain
        current_hash = self.domain.compute_profile_hash(skill_profile)

        # 3. Check cached report — if hash matches, return cached
        cached = await self.repo.get_cached_report(user_id)
        if cached and cached.profile_hash == current_hash:
            return cached

        # 4. Load job listings from repo
        jobs = await self.repo.get_job_listings_for_roles(target_roles, state)
        
        # Extract required skills and their frequency
        required_skills_map = {} # skill -> count
        for job in jobs:
            for skill in job.required_skills:
                required_skills_map[skill] = required_skills_map.get(skill, 0) + 1
        
        total_jobs = len(jobs) or 1
        
        # 5. Classify skills via domain (strength/gap/partial)
        # 6. Compute priority scores via domain
        gaps = []
        user_skills_dict = {s.skill_name.lower(): s for s in skill_profile.skills}
        
        for skill_name, count in required_skills_map.items():
            freq_pct = count / total_jobs
            user_skill = user_skills_dict.get(skill_name.lower())
            
            status = self.domain.classify_skill_status(user_skill, skill_name)
            
            if status in ["gap", "partial"]:
                user_prof = user_skill.proficiency if user_skill else 0
                # Assuming learnability_factor=1.0 for now, refine with AI later
                priority = self.domain.compute_priority_score(freq_pct, user_prof, 1.0)
                
                gaps.append(GapEntry(
                    skill_name=skill_name,
                    priority_score=priority,
                    status=status,
                    user_proficiency=user_prof,
                    required_proficiency=3, # Default required
                    learnability_weeks=2.0, # Default, will be updated by AI
                    reasons=[f"Required in {int(freq_pct*100)}% of local jobs"]
                ))

        # 7. Call ai_pipeline for learnability_weeks + messages
        if gaps:
            learnability_map = await self.ai.analyze_learnability([g.skill_name for g in gaps])
            for gap in gaps:
                gap.learnability_weeks = learnability_map.get(gap.skill_name, 2.0)
        
        # 8. Load resources from repo
        resources = await self.repo.get_resources_for_skills([g.skill_name for g in gaps])

        # 9. Build roadmap via domain
        ranked_gaps = self.domain.rank_gaps(gaps)
        roadmap = self.domain.build_roadmap_weeks(ranked_gaps, resources)

        # 10. Save report to repo
        report_data = {
            "gaps": [g.__dict__ for g in ranked_gaps],
            "roadmap": [r.__dict__ for r in roadmap],
            "mentorship_msg": await self.ai.generate_mentorship_message(ranked_gaps[0].skill_name) if ranked_gaps else ""
        }
        
        report = GapAnalysisReport(
            user_id=user_id,
            report_data=report_data,
            profile_hash=current_hash
        )
        await self.repo.save_report(report)

        # 11. Return report
        return report
