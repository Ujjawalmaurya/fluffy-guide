"""
Onboarding service — orchestrates the 5-step wizard.
Calls question_engine for AI-generated questions.
Delegates DB ops to repository.
"""
from app.modules.onboarding.repository import OnboardingRepository
from app.modules.onboarding.question_engine import generate_questions
from app.modules.ai_chat.providers.base import IStructuredProvider
from app.schemas.request.onboarding import (
    UserTypeRequest, ProfileRequest, PreferencesRequest, StudentOnboardingRequest, BlueCollarOnboardingRequest,
    InformalWorkerOnboardingRequest, EmployerOnboardingRequest, NGOOnboardingRequest, GovtOfficerOnboardingRequest,
    GenerateQuestionsRequest, SubmitAnswersRequest
)
from app.shared.exceptions import OnboardingStepIncomplete
from app.core.logger import get_logger 

log = get_logger("ONBOARDING")

VALID_USER_TYPES = {
    "individual_youth", "individual_bluecollar", "individual_informal",
    "org_ngo", "org_employer", "org_govt",
}


class OnboardingService:
    def __init__(self, repo: OnboardingRepository, llm_provider: IStructuredProvider):
        self.repo = repo
        self.llm_provider = llm_provider

    def _calculate_completion(self, data, mandatory_fields: list[str], optional_fields: list[str]) -> int:
        """Generic completion percentage calculator."""
        data_dict = data.model_dump()
        
        # Mandatory: 60% total (split equally)
        m_count = len(mandatory_fields)
        m_filled = sum(1 for f in mandatory_fields if data_dict.get(f))
        m_score = int((m_filled / m_count) * 60) if m_count > 0 else 60
        
        # Optional: 40% total (split equally)
        o_count = len(optional_fields)
        o_filled = 0
        for f in optional_fields:
            val = data_dict.get(f)
            if val is not None and (not isinstance(val, (list, str)) or len(val) > 0):
                o_filled += 1
        o_score = int((o_filled / o_count) * 40) if o_count > 0 else 40
        
        return min(m_score + o_score, 100)

    async def _save_and_mark_progress(self, user_id: str, data, mandatory: list[str], optional: list[str], step: int = 5, auto_done: bool = True):
        """Unified helper to save profile and handle onboarding state."""
        percentage = self._calculate_completion(data, mandatory, optional)
        await self.repo.save_user_profile(user_id, data.model_dump())
        
        is_done = auto_done or percentage >= 60
        if is_done:
            await self.repo.mark_onboarding_done(user_id)
            log.info(f"Onboarding COMPLETED for user={user_id}, percentage={percentage}%")
        else:
            await self.repo.update_user_onboarding(user_id, step, percentage)
            log.info(f"Onboarding progress: user={user_id}, step={step}, percentage={percentage}%")
            
        return {
            "percentage": percentage, 
            "onboarding_done": is_done,
            "status": "completed" if is_done else "in_progress"
        }

    async def save_student_onboarding(self, user_id: str, data: StudentOnboardingRequest, step: int):
        mandatory = ["full_name", "state", "education_level"]
        optional = ["age", "gender", "city", "preferred_job_location", "stream", "institution_name", "career_interests", "languages_known"]
        return await self._save_and_mark_progress(user_id, data, mandatory, optional, step, auto_done=(step >= 4))

    async def save_blue_collar_onboarding(self, user_id: str, data: BlueCollarOnboardingRequest, step: int):
        mandatory = ["full_name", "state", "primary_trade"]
        optional = ["age", "gender", "city", "village_district", "secondary_skills", "years_experience", "is_currently_employed", "preferred_work_radius", "owns_smartphone", "languages_known"]
        return await self._save_and_mark_progress(user_id, data, mandatory, optional, step, auto_done=(step >= 5))

    async def save_informal_worker_onboarding(self, user_id: str, data: InformalWorkerOnboardingRequest, step: int = 5):
        mandatory = ["full_name", "state", "current_work_type"]
        optional = ["age", "gender", "city_village", "monthly_income", "interests", "languages_known"]
        return await self._save_and_mark_progress(user_id, data, mandatory, optional, step=step)

    async def save_employer_onboarding(self, user_id: str, data: EmployerOnboardingRequest):
        mandatory = ["company_name", "industry_sector", "state", "city"]
        optional = ["contact_person_name", "designation", "company_size", "roles_hiring_for", "preferred_skills", "work_type_offered"]
        res = await self._save_and_mark_progress(user_id, data, mandatory, optional, step=5)
        res["redirect"] = "/employer-dashboard"
        return res

    async def save_ngo_onboarding(self, user_id: str, data: NGOOnboardingRequest):
        mandatory = ["org_name", "focus_sectors", "coverage_areas"]
        optional = ["registration_number", "beneficiary_types", "contact_name", "contact_designation"]
        res = await self._save_and_mark_progress(user_id, data, mandatory, optional, step=5)
        res["redirect"] = "/ngo-dashboard"
        return res

    async def save_govt_onboarding(self, user_id: str, data: GovtOfficerOnboardingRequest):
        mandatory = ["full_name", "department", "state_jurisdiction"]
        optional = ["designation", "access_level", "district_jurisdiction"]
        res = await self._save_and_mark_progress(user_id, data, mandatory, optional, step=5)
        res["redirect"] = "/govt-dashboard"
        return res

    async def set_user_type(self, user_id: str, data: UserTypeRequest):
        # Fetch current user to check if user_type is already set (immutability rule)
        user = await self.repo.get_user(user_id)
        if user and user.get("user_type"):
            from app.shared.exceptions import Conflict
            raise Conflict(f"User role is already set to {user['user_type']} and cannot be changed.")

        if data.user_type not in VALID_USER_TYPES:
            raise OnboardingStepIncomplete(f"Invalid user type: {data.user_type}")
        await self.repo.set_user_type(user_id, data.user_type)
        await self.repo.upsert_state(user_id, current_step=2, completed_steps=[1])
        log.info(f"User type set: {data.user_type} for user={user_id}")

    async def save_profile(self, user_id: str, data: ProfileRequest):
        """Generic profile save (Step 2 in some flows)."""
        await self.repo.save_user_profile(user_id, data.model_dump())
        await self.repo.upsert_state(user_id, current_step=3, completed_steps=[1, 2])
        log.info(f"Profile saved for user={user_id}")

    async def save_preferences(self, user_id: str, data: PreferencesRequest):
        """Generic preferences save (Step 3 in some flows)."""
        await self.repo.save_user_profile(user_id, data.model_dump())
        await self.repo.upsert_state(user_id, current_step=4, completed_steps=[1, 2, 3])
        log.info(f"Preferences saved for user={user_id}")

    async def generate_questions(self, user_id: str, data: GenerateQuestionsRequest) -> list[dict]:
        user = await self.repo.get_user(user_id)
        if not user or not user.get("user_type"):
            raise OnboardingStepIncomplete("Complete step 1 (user type) first.")

        prefs = await self.repo.get_preferences(user_id)
        career_interests = prefs.get("career_interests", []) if prefs else []

        # Get state from profile
        profile_res = self.repo.db.table("user_profiles").select("state").eq("user_id", user_id).execute()
        state = profile_res.data[0]["state"] if profile_res.data else "India"

        questions = await generate_questions(
            llm_provider=self.llm_provider,
            user_type=user["user_type"],
            state=state,
            career_interests=career_interests,
            language=data.language,
        )

        session = await self.repo.create_questionnaire_session(user_id, data.language, questions)
        log.info(f"Generated {len(questions)} questions for {user['user_type']} via Ollama")
        return questions

    async def submit_answers(self, user_id: str, data: SubmitAnswersRequest) -> str:
        session = await self.repo.get_latest_session(user_id)
        if not session:
            raise OnboardingStepIncomplete("Generate questions first (step 4).")

        answers_list = [a.model_dump() for a in data.answers]
        await self.repo.submit_answers(session["id"], answers_list)
        await self.repo.upsert_state(user_id, current_step=5, completed_steps=[1, 2, 3, 4])
        log.info(f"Answers submitted. session_id={session['id']}. Ready for processing.")
        return session["id"]

    async def get_state(self, user_id: str) -> dict:
        state = await self.repo.get_state(user_id)
        if not state:
            return {"current_step": 1, "completed_steps": [], "step_data": {}}
        return state
