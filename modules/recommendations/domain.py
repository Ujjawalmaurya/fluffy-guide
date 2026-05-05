import difflib
from typing import List, Optional

class JobMatchDomain:
    @staticmethod
    def compute_skill_overlap(user_skills: List[str], job_required_skills: List[str]) -> float:
        if not job_required_skills:
            return 0.0
            
        matched_count = 0
        user_skills_lower = [s.lower().strip() for s in user_skills]
        
        for req_skill in job_required_skills:
            req_skill_lower = req_skill.lower().strip()
            # Direct match first
            if req_skill_lower in user_skills_lower:
                matched_count += 1
                continue
            
            # Fuzzy match
            for user_skill in user_skills_lower:
                ratio = difflib.SequenceMatcher(None, req_skill_lower, user_skill).ratio()
                if ratio > 0.8:
                    matched_count += 1
                    break
                    
        return matched_count / len(job_required_skills)

    @staticmethod
    def compute_location_score(user_state: str, user_city: str, job_state: str, job_city: str, willing_to_relocate: bool = False) -> float:
        u_state = user_state.lower().strip()
        u_city = user_city.lower().strip()
        j_state = job_state.lower().strip()
        j_city = job_city.lower().strip()
        
        if u_city == j_city and u_state == j_state:
            return 1.0
        
        if u_state == j_state:
            return 0.7
            
        if willing_to_relocate:
            return 0.4
            
        return 0.1

    @staticmethod
    def compute_salary_overlap(user_min: Optional[int], user_max: Optional[int], job_min: Optional[int], job_max: Optional[int]) -> float:
        # Handle None values (job has no salary listed)
        if job_min is None or job_max is None:
            return 0.5
            
        # If user hasn't specified range, neutral
        if user_min is None or user_max is None:
            return 0.5
            
        # Overlap logic
        overlap_min = max(user_min, job_min)
        overlap_max = min(user_max, job_max)
        
        if overlap_min > overlap_max:
            return 0.0
            
        user_range = user_max - user_min
        if user_range <= 0:
            return 1.0 if (user_min >= job_min and user_min <= job_max) else 0.0
            
        overlap_range = overlap_max - overlap_min
        
        if overlap_range >= user_range:
            return 1.0
            
        return overlap_range / user_range

    @staticmethod
    def compute_composite_score(skill_overlap: float, location_score: float, salary_overlap: float, work_mode_match: bool) -> float:
        # Weights: skill=0.50, location=0.25, salary=0.15, work_mode=0.10
        score = (
            (skill_overlap * 0.50) +
            (location_score * 0.25) +
            (salary_overlap * 0.15) +
            ((1.0 if work_mode_match else 0.0) * 0.10)
        )
        return float(score * 100.0)

    @staticmethod
    def apply_user_type_boost(score: float, user_type: str, job_category: str) -> float:
        # individual_bluecollar + vocational job category → +5 points
        # individual_informal + self_employment category → +5 points
        # individual_youth + entry_level job → +3 points
        boost = 0.0
        if user_type == "individual_bluecollar" and job_category == "vocational":
            boost = 5.0
        elif user_type == "individual_informal" and job_category == "self_employment":
            boost = 5.0
        elif user_type == "individual_youth" and job_category == "entry_level":
            boost = 3.0
            
        return min(100.0, score + boost)
