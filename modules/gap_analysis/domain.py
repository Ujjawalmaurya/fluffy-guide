import hashlib
import json
from typing import Literal, List, Dict, Optional
from dataclasses import dataclass

@dataclass
class SkillEntry:
    skill_name: str
    proficiency: int
    confidence: float = 1.0
    source: str = "manual"

@dataclass
class GapEntry:
    skill_name: str
    priority_score: float
    status: Literal["gap", "partial"]
    user_proficiency: int
    required_proficiency: int
    learnability_weeks: float
    reasons: List[str]

@dataclass
class LearningResource:
    title: str
    url: str
    provider: str
    duration: str
    type: str

@dataclass
class RoadmapWeek:
    week_number: int
    focus_skills: List[str]
    goal: str
    actions: List[str]
    resources: List[LearningResource]
    milestone: str

@dataclass
class UserSkillProfile:
    skills: List[SkillEntry]

class GapAnalysisDomain:
    @staticmethod
    def compute_priority_score(frequency_pct: float, user_proficiency: int, learnability_factor: float) -> float:
        # Formula: frequency_pct × (1 - user_proficiency/5) × learnability_factor
        score = frequency_pct * (1 - user_proficiency / 5.0) * learnability_factor
        return float(max(0.0, min(1.0, score)))

    @staticmethod
    def classify_skill_status(user_skill: Optional[SkillEntry], required_skill: str, job_required_proficiency: int = 3) -> Literal["strength", "gap", "partial"]:
        if not user_skill:
            return "gap"
        
        if user_skill.proficiency >= job_required_proficiency:
            return "strength"
        
        return "partial"

    @staticmethod
    def rank_gaps(gaps: List[GapEntry]) -> List[GapEntry]:
        # Sort by priority_score DESC
        # Tiebreak: learnability_weeks ASC (learn faster first)
        return sorted(gaps, key=lambda x: (-x.priority_score, x.learnability_weeks))

    @staticmethod
    def compute_profile_hash(skill_profile: UserSkillProfile) -> str:
        # SHA256 of sorted skill names + proficiency values
        sorted_skills = sorted(skill_profile.skills, key=lambda x: x.skill_name.lower())
        hash_input = "|".join([f"{s.skill_name.lower().strip()}:{s.proficiency}" for s in sorted_skills])
        return hashlib.sha256(hash_input.encode()).hexdigest()

    @staticmethod
    def build_roadmap_weeks(ranked_gaps: List[GapEntry], resources: Dict[str, List[LearningResource]]) -> List[RoadmapWeek]:
        # Max 2 skills per week
        # Total roadmap: max 12 weeks
        # Week 1 always = highest priority gap
        
        roadmap: List[RoadmapWeek] = []
        max_weeks = 12
        skills_per_week = 2
        
        # We only build roadmap for gaps and partials
        current_gaps = [g for g in ranked_gaps if g.status in ["gap", "partial"]]
        
        if not current_gaps:
            return []

        # Consume gaps to fill weeks
        gap_idx = 0
        for week_num in range(1, max_weeks + 1):
            if gap_idx >= len(current_gaps):
                break
                
            week_skills = current_gaps[gap_idx:gap_idx + skills_per_week]
            gap_idx += skills_per_week
            
            skill_names = [s.skill_name for s in week_skills]
            week_resources = []
            for s_name in skill_names:
                week_resources.extend(resources.get(s_name, []))
            
            # Simple heuristic for goals/actions/milestones
            goal = f"Master {', '.join(skill_names)}"
            actions = [f"Complete {s_name} course" for s_name in skill_names]
            milestone = f"Proficient in {skill_names[0]}"
            
            roadmap.append(RoadmapWeek(
                week_number=week_num,
                focus_skills=skill_names,
                goal=goal,
                actions=actions,
                resources=week_resources[:3], # Cap resources per week
                milestone=milestone
            ))
            
        return roadmap
