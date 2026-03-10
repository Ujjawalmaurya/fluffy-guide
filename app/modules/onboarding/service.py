"""
Onboarding service — orchestrates the 5-step wizard.
Calls question_engine for AI-generated questions.
Delegates DB ops to repository.
"""
from app.modules.onboarding.repository import OnboardingRepository
from app.modules.onboarding.question_engine import generate_questions
from app.modules.onboarding.schemas import (
    UserTypeIn, ProfileIn, PreferencesIn, GenerateQuestionsIn, SubmitAnswersIn
)
from app.shared.exceptions import OnboardingStepIncomplete
from app.core.logger import get_logger

log = get_logger("ONBOARDING")

VALID_USER_TYPES = {
    "individual_youth", "individual_bluecollar", "individual_informal",
    "org_ngo", "org_employer", "org_govt",
}


class OnboardingService:
    def __init__(self, repo: OnboardingRepository):
        self.repo = repo

    def set_user_type(self, user_id: str, data: UserTypeIn):
        if data.user_type not in VALID_USER_TYPES:
            raise OnboardingStepIncomplete(f"Invalid user type: {data.user_type}")
        self.repo.set_user_type(user_id, data.user_type)
        self.repo.upsert_state(user_id, current_step=2, completed_steps=[1])
        log.info(f"User type set: {data.user_type} for user={user_id}")

    def save_profile(self, user_id: str, data: ProfileIn):
        self.repo.upsert_profile(user_id, data.model_dump())
        self.repo.upsert_state(user_id, current_step=3, completed_steps=[1, 2])
        log.info(f"Profile saved for user={user_id}, location={data.city}, {data.state}")

    def save_preferences(self, user_id: str, data: PreferencesIn):
        self.repo.upsert_preferences(user_id, data.model_dump())
        self.repo.upsert_state(user_id, current_step=4, completed_steps=[1, 2, 3])
        log.info(f"Preferences saved. career_interests={data.career_interests}")

    async def generate_questions(self, user_id: str, data: GenerateQuestionsIn) -> list[dict]:
        user = self.repo.get_user(user_id)
        if not user or not user.get("user_type"):
            raise OnboardingStepIncomplete("Complete step 1 (user type) first.")

        prefs = self.repo.get_preferences(user_id)
        career_interests = prefs.get("career_interests", []) if prefs else []

        # Get state from profile
        profile_res = self.repo.db.table("user_profiles").select("state").eq("user_id", user_id).execute()
        state = profile_res.data[0]["state"] if profile_res.data else "India"

        questions = await generate_questions(
            user_type=user["user_type"],
            state=state,
            career_interests=career_interests,
            language=data.language,
        )

        session = self.repo.create_questionnaire_session(user_id, data.language, questions)
        log.info(f"Generated {len(questions)} questions for {user['user_type']} via SarvamAI")
        return questions

    def submit_answers(self, user_id: str, data: SubmitAnswersIn) -> str:
        session = self.repo.get_latest_session(user_id)
        if not session:
            raise OnboardingStepIncomplete("Generate questions first (step 4).")

        answers_list = [a.model_dump() for a in data.answers]
        self.repo.submit_answers(session["id"], answers_list)
        self.repo.upsert_state(user_id, current_step=5, completed_steps=[1, 2, 3, 4])
        log.info(f"Answers submitted. session_id={session['id']}. Ready for processing.")
        return session["id"]

    def get_state(self, user_id: str) -> dict:
        state = self.repo.get_state(user_id)
        if not state:
            return {"current_step": 1, "completed_steps": [], "step_data": {}}
        return state
