"""
Onboarding service — orchestrates the 5-step wizard.
Calls question_engine for AI-generated questions.
Delegates DB ops to repository.
"""
from app.modules.onboarding.repository import OnboardingRepository
from app.modules.onboarding.question_engine import generate_questions
from app.modules.ai_chat.providers.base import ILLMProvider
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
    def __init__(self, repo: OnboardingRepository, llm_provider: ILLMProvider):
        self.repo = repo
        self.llm_provider = llm_provider

    def calculate_student_completion(self, data: StudentOnboardingRequest) -> int:
        """
        Req: name, state, education_level (20% each = 60%)
        Opt: age, gender, city, job_pref, stream, institution, interests, languages (5% each = 40%)
        """
        percentage = 0
        # Mandatory
        if data.full_name: percentage += 20
        if data.state: percentage += 20
        if data.education_level: percentage += 20
        
        # Optional
        if data.age: percentage += 5
        if data.gender: percentage += 5
        if data.city: percentage += 5
        if data.preferred_job_location: percentage += 5
        if data.stream: percentage += 5
        if data.institution_name: percentage += 5
        if data.career_interests: percentage += 5
        if data.languages_known: percentage += 5
        
        return min(percentage, 100)

    async def save_student_onboarding(self, user_id: str, data: StudentOnboardingRequest, step: int):
        """Save student profile data and update onboarding progress."""
        percentage = self.calculate_student_completion(data)
        await self.repo.save_student_profile(user_id, data.model_dump())
        
        log.info(f"Student onboarding: user={user_id}, step={step}, percentage={percentage}%")
        
        # In the new flow, the frontend sends everything at once. 
        # We mark it done if step=4 (final step for student) OR if we received a substantially complete profile.
        if step >= 4 or percentage >= 60:
            await self.repo.mark_onboarding_done(user_id)
            log.info(f"Student onboarding COMPLETED for user={user_id}")
        else:
            await self.repo.update_user_onboarding(user_id, step, percentage)
            log.info(f"Student onboarding progress updated for user={user_id}")

    def calculate_blue_collar_completion(self, data: BlueCollarOnboardingRequest) -> int:
        """
        Req: name, state, primary_trade (20% each = 60%)
        Opt: age, gender, city, village, sec_skills, exp, employed, radius, smartphone, languages (4% each = 40%)
        """
        percentage = 0
        # Mandatory
        if data.full_name: percentage += 20
        if data.state: percentage += 20
        if data.primary_trade: percentage += 20
        
        # Optional
        if data.age: percentage += 4
        if data.gender: percentage += 4
        if data.city: percentage += 4
        if data.village_district: percentage += 4
        if data.secondary_skills: percentage += 4
        if data.years_experience: percentage += 4
        if data.is_currently_employed: percentage += 4
        if data.preferred_work_radius: percentage += 4
        if data.owns_smartphone is not None: percentage += 4
        if data.languages_known: percentage += 4
        
        return min(percentage, 100)

    async def save_blue_collar_onboarding(self, user_id: str, data: BlueCollarOnboardingRequest, step: int):
        """Save blue collar profile data and update onboarding progress."""
        percentage = self.calculate_blue_collar_completion(data)
        await self.repo.save_blue_collar_profile(user_id, data.model_dump())
        
        log.info(f"Blue collar onboarding: user={user_id}, step={step}, percentage={percentage}%")
        
        if step >= 5 or percentage >= 60:
            await self.repo.mark_onboarding_done(user_id)
            log.info(f"Blue collar onboarding COMPLETED for user={user_id}")
        else:
            await self.repo.update_user_onboarding(user_id, step, percentage)
            log.info(f"Blue collar onboarding progress updated for user={user_id}")

    def calculate_informal_worker_completion(self, data: InformalWorkerOnboardingRequest) -> int:
        mandatory_fields = ['full_name', 'state', 'current_work_type']
        optional_fields = ['age', 'gender', 'city_village', 'monthly_income', 'interests', 'languages_known']
        
        # Base 60% for mandatory
        mandatory_score = 60
        
        # 40% for optional
        optional_count = len(optional_fields)
        filled_optional = 0
        
        data_dict = data.model_dump()
        for field in optional_fields:
            val = data_dict.get(field)
            if val and (not isinstance(val, list) or len(val) > 0):
                filled_optional += 1
                
        optional_score = int((filled_optional / optional_count) * 40)
        return mandatory_score + optional_score

    async def save_informal_worker_onboarding(self, user_id: str, data: InformalWorkerOnboardingRequest):
        percentage = self.calculate_informal_worker_completion(data)
        
        await self.repo.save_informal_worker_profile(user_id, data.model_dump())
        
        await self.repo.mark_onboarding_done(user_id)
        
        return {"percentage": percentage, "status": "onboarded"}

    def calculate_employer_completion(self, data: EmployerOnboardingRequest) -> int:
        mandatory_fields = ['company_name', 'industry_sector', 'state', 'city']
        optional_fields = ['contact_person_name', 'designation', 'company_size', 'roles_hiring_for', 'preferred_skills', 'work_type_offered']
        
        # Base 60% for mandatory
        mandatory_score = 60
        
        # 40% for optional
        optional_count = len(optional_fields)
        filled_optional = 0
        
        data_dict = data.model_dump()
        for field in optional_fields:
            val = data_dict.get(field)
            if val and (not isinstance(val, list) or len(val) > 0):
                filled_optional += 1
                
        optional_score = int((filled_optional / optional_count) * 40)
        return mandatory_score + optional_score

    async def save_employer_onboarding(self, user_id: str, data: EmployerOnboardingRequest):
        percentage = self.calculate_employer_completion(data)
        
        await self.repo.save_employer_profile(user_id, data.model_dump())
        
        await self.repo.mark_onboarding_done(user_id)
        
        return {"percentage": percentage, "status": "onboarded", "redirect": "/employer-dashboard"}

    def calculate_ngo_completion(self, data: NGOOnboardingRequest) -> int:
        mandatory_fields = ['org_name', 'focus_sectors', 'coverage_areas']
        optional_fields = ['registration_number', 'beneficiary_types', 'contact_name', 'contact_designation']
        
        # Base 60% for mandatory
        mandatory_score = 60
        
        # 40% for optional
        optional_count = len(optional_fields)
        filled_optional = 0
        
        data_dict = data.model_dump()
        for field in optional_fields:
            val = data_dict.get(field)
            if val and (not isinstance(val, list) or len(val) > 0):
                filled_optional += 1
                
        optional_score = int((filled_optional / optional_count) * 40)
        return mandatory_score + optional_score

    async def save_ngo_onboarding(self, user_id: str, data: NGOOnboardingRequest):
        percentage = self.calculate_ngo_completion(data)
        
        await self.repo.save_ngo_profile(user_id, data.model_dump())
        
        await self.repo.mark_onboarding_done(user_id)
        
        return {"percentage": percentage, "status": "onboarded", "redirect": "/ngo-dashboard"}

    def calculate_govt_completion(self, data: GovtOfficerOnboardingRequest) -> int:
        mandatory_fields = ['full_name', 'department', 'state_jurisdiction']
        optional_fields = ['designation', 'access_level', 'district_jurisdiction']
        
        # Base 60% for mandatory
        mandatory_score = 60
        
        # 40% for optional
        optional_count = len(optional_fields)
        filled_optional = 0
        
        data_dict = data.model_dump()
        for field in optional_fields:
            val = data_dict.get(field)
            if val and (not isinstance(val, list) or len(val) > 0):
                filled_optional += 1
                
        optional_score = int((filled_optional / optional_count) * 40)
        return mandatory_score + optional_score

    async def save_govt_onboarding(self, user_id: str, data: GovtOfficerOnboardingRequest):
        percentage = self.calculate_govt_completion(data)
        
        await self.repo.save_govt_profile(user_id, data.model_dump())
        
        await self.repo.mark_onboarding_done(user_id)
        
        return {"percentage": percentage, "status": "onboarded", "redirect": "/govt-dashboard"}

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
        await self.repo.upsert_profile(user_id, data.model_dump())
        await self.repo.upsert_state(user_id, current_step=3, completed_steps=[1, 2])
        log.info(f"Profile saved for user={user_id}, location={data.city}, {data.state}")

    async def save_preferences(self, user_id: str, data: PreferencesRequest):
        await self.repo.upsert_preferences(user_id, data.model_dump())
        await self.repo.upsert_state(user_id, current_step=4, completed_steps=[1, 2, 3])
        log.info(f"Preferences saved. career_interests={data.career_interests}")

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
