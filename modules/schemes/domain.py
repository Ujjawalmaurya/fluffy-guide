from typing import List, Dict, Optional
from dataclasses import dataclass, field

@dataclass
class UserProfile:
    age: int
    state: str
    education_level: str # e.g., "10th", "12th", "Graduate"

@dataclass
class SchemeEligibilityCriteria:
    min_age: int = 18
    max_age: int = 45
    states: List[str] = field(default_factory=list) # Empty = National
    min_education: Optional[str] = None # e.g., "10th"

@dataclass
class GovernmentScheme:
    id: str
    title: str
    eligibility: SchemeEligibilityCriteria

@dataclass
class EligibilityResult:
    eligible: bool
    reasons: List[str]
    missing: List[str]

@dataclass
class RankedScheme:
    scheme: GovernmentScheme
    eligibility_result: EligibilityResult

class SchemeDomain:
    EDUCATION_ORDER = ["None", "8th", "10th", "12th", "Diploma", "Graduate", "Postgraduate"]

    @staticmethod
    def _is_education_sufficient(user_edu: str, required_edu: Optional[str]) -> bool:
        if not required_edu or required_edu == "None":
            return True
        
        try:
            user_idx = SchemeDomain.EDUCATION_ORDER.index(user_edu)
            req_idx = SchemeDomain.EDUCATION_ORDER.index(required_edu)
            return user_idx >= req_idx
        except ValueError:
            return False

    @staticmethod
    def check_eligibility(user_profile: UserProfile, scheme: GovernmentScheme) -> EligibilityResult:
        reasons = []
        missing = []
        
        # Age check
        if scheme.eligibility.min_age <= user_profile.age <= scheme.eligibility.max_age:
            reasons.append(f"Age {user_profile.age} is within range {scheme.eligibility.min_age}-{scheme.eligibility.max_age}")
        else:
            missing.append("age")
            
        # State check
        if not scheme.eligibility.states or user_profile.state in scheme.eligibility.states:
            reasons.append(f"State {user_profile.state} is eligible")
        else:
            missing.append("state")
            
        # Education check
        if SchemeDomain._is_education_sufficient(user_profile.education_level, scheme.eligibility.min_education):
            reasons.append(f"Education level {user_profile.education_level} is sufficient")
        else:
            missing.append("education")
            
        eligible = len(missing) == 0
        return EligibilityResult(eligible=eligible, reasons=reasons, missing=missing)

    @staticmethod
    def rank_schemes(schemes: List[GovernmentScheme], user_profile: UserProfile) -> List[RankedScheme]:
        results = []
        for s in schemes:
            res = SchemeDomain.check_eligibility(user_profile, s)
            # Exclude if more than 1 criterion missing (ineligible)
            if res.eligible or len(res.missing) == 1:
                results.append(RankedScheme(scheme=s, eligibility_result=res))
                
        # Fully eligible first, then partially
        return sorted(results, key=lambda x: (not x.eligibility_result.eligible))
