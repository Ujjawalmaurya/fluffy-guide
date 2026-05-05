from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class SkillEntry:
    skill_name: str
    proficiency: int
    confidence: float = 1.0
    source: str = "manual"

@dataclass
class UserSkillProfile:
    skills: List[SkillEntry]

class SkillMergeDomain:
    @staticmethod
    def resolve_proficiency_conflict(resume_entry: SkillEntry, assessment_entry: SkillEntry) -> SkillEntry:
        # Weighted average: assessment × 0.6 + resume × 0.4
        new_proficiency = int(round((assessment_entry.proficiency * 0.6) + (resume_entry.proficiency * 0.4)))
        new_confidence = max(resume_entry.confidence, assessment_entry.confidence)
        
        return SkillEntry(
            skill_name=assessment_entry.skill_name, # Names should be same or similar enough
            proficiency=new_proficiency,
            confidence=new_confidence,
            source="both"
        )

    @staticmethod
    def merge_skill_lists(resume_skills: List[SkillEntry], assessment_skills: List[SkillEntry]) -> List[SkillEntry]:
        merged_dict: Dict[str, SkillEntry] = {}
        
        # Add resume skills
        for s in resume_skills:
            merged_dict[s.skill_name.lower().strip()] = s
            
        # Add assessment skills with conflict resolution
        for s in assessment_skills:
            key = s.skill_name.lower().strip()
            if key in merged_dict:
                merged_dict[key] = SkillMergeDomain.resolve_proficiency_conflict(merged_dict[key], s)
            else:
                merged_dict[key] = s
                
        # Sort final list by proficiency DESC
        return sorted(merged_dict.values(), key=lambda x: x.proficiency, reverse=True)

    @staticmethod
    def compute_profile_completeness(skill_profile: UserSkillProfile, has_resume: bool, assessment_done: bool) -> float:
        # Skills count: min(len(skills)/10, 0.5) → max 50% from skills alone
        skills_score = min(len(skill_profile.skills) / 10.0, 0.5)
        
        # Resume: +25% if has_resume
        resume_score = 0.25 if has_resume else 0.0
        
        # Assessment: +25% if assessment_done
        assessment_score = 0.25 if assessment_done else 0.0
        
        return float(skills_score + resume_score + assessment_score)
