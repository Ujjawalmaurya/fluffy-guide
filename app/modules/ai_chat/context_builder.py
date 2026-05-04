import json
from typing import Any, Dict
from app.modules.ai_chat.context import (
    BaseContext, StudentContext, BlueCollarContext, InformalWorkerContext,
    EmployerContext, NGOContext, GovtOfficerContext
)

def build_context_json(data: Dict[str, Any]) -> str:
    """
    Main entry point to build the context JSON for the LLM.
    'data' is the dictionary returned by ChatRepository.get_full_user_data.
    """
    user = data.get("user", {})
    profile = data.get("profile", {})
    prefs = data.get("preferences", {})
    skills_data = data.get("skills", {})
    gaps_data = data.get("gaps", {})
    
    role = user.get("user_type", "individual_youth")
    user_id = user.get("id", "")
    
    # Common fields
    common = {
        "user_id": user_id,
        "role": role,
        "full_name": profile.get("full_name") or "User",
        "state": profile.get("state") or "India",
        "city": profile.get("city"),
        "languages": profile.get("languages") or [],
        "skills": skills_data.get("skills") or [],
        "gaps": gaps_data.get("gaps") or [],
        "strengths": gaps_data.get("strengths") or [],
        "onboarding_done": user.get("onboarding_done", False),
        "assessment_done": user.get("quick_assessment_done", False)
    }

    try:
        if role == "individual_youth":
            context = StudentContext(
                **common,
                age=profile.get("age"),
                education_level=profile.get("education_level") or "Not specified",
                stream=profile.get("stream"),
                institution=profile.get("institution_name"),
                career_interests=prefs.get("career_interests") or []
            )
        elif role == "individual_bluecollar":
            context = BlueCollarContext(
                **common,
                primary_trade=profile.get("primary_trade") or "Not specified",
                secondary_skills=profile.get("secondary_skills") or [],
                experience=profile.get("years_experience"),
                is_employed=profile.get("is_currently_employed"),
                work_radius=profile.get("preferred_work_radius") or "Local",
                owns_smartphone=profile.get("owns_smartphone", True)
            )
        elif role == "individual_informal":
            context = InformalWorkerContext(
                **common,
                work_type=profile.get("current_work_type") or "Not specified",
                income_range=profile.get("monthly_income"),
                digital_literacy=profile.get("digital_literacy") or "Basic",
                owns_smartphone=profile.get("owns_smartphone", True),
                interests=profile.get("interests") or []
            )
        elif role == "org_employer":
            context = EmployerContext(
                contact_name=profile.get("contact_person_name") or "User",
                designation=profile.get("designation"),
                company_name=profile.get("company_name") or "Company",
                industry=profile.get("industry_sector") or "Various",
                size=profile.get("company_size"),
                location=f"{profile.get('city')}, {profile.get('state')}",
                hiring_roles=profile.get("roles_hiring_for") or [],
                required_skills=profile.get("preferred_skills") or []
            )
        elif role == "org_ngo":
            context = NGOContext(
                org_name=profile.get("org_name") or "NGO",
                focus_sectors=profile.get("focus_sectors") or [],
                coverage_areas=profile.get("coverage_areas") or [],
                beneficiary_types=profile.get("beneficiary_types") or [],
                contact_person=profile.get("contact_name") or "User"
            )
        elif role == "org_govt":
            context = GovtOfficerContext(
                full_name=profile.get("full_name") or "Officer",
                designation=profile.get("designation"),
                department=profile.get("department") or "Government",
                access_level=profile.get("access_level") or "State",
                jurisdiction=f"{profile.get('state_jurisdiction')} {profile.get('district_jurisdiction')}"
            )
        else:
            # Fallback to base context
            context = BaseContext(**common)
            
        return context.model_dump_json()
    except Exception as e:
        # If schema mapping fails, return at least the common data as JSON
        return json.dumps(common)
