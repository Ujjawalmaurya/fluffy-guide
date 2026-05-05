from typing import List, Optional
from datetime import datetime, timedelta

class AssessmentDomain:
    @staticmethod
    def should_advance_phase(phase: int, answers_in_phase: int, signals: List[str]) -> bool:
        # Never advance if current phase has < 1 answer
        if answers_in_phase < 1:
            return False
            
        if phase == 1:
            # Phase 1: advance after 2 answers OR if situation context is clear
            return answers_in_phase >= 2 or "situation_clear" in signals
            
        if 2 <= phase <= 4:
            # Phases 2–4: advance after 2–3 answers
            return answers_in_phase >= 2
            
        if phase == 5:
            # Phase 5: always last, max 2 questions
            # This logic usually handles ending the assessment
            return answers_in_phase >= 2
            
        return False

    @staticmethod
    def extract_phase_instruction(phase: int, user_type: str) -> str:
        instructions = {
            1: "Identify user's current situation and basic background.",
            2: "Inventory user's technical and soft skills.",
            3: "Assess user's preferred work style and environment.",
            4: "Explore user's future goals and immediate blockers.",
            5: "Address any remaining gaps or specific user interests (Wildcard)."
        }
        
        base_instruction = instructions.get(phase, "General assessment.")
        
        if user_type == "individual_bluecollar":
            base_instruction += " Use Hindi-friendly, simpler phrasing. Focus on practical experience."
        elif user_type == "individual_informal":
            base_instruction += " Use extremely simple language, avoid all professional jargon. Focus on daily tasks."
        
        return base_instruction

    @staticmethod
    def compute_retake_allowed(retake_number: int, max_retakes: int, last_completed_at: Optional[datetime]) -> bool:
        # retake_number < max_retakes AND
        # last_completed_at is None OR > 7 days ago
        if retake_number >= max_retakes:
            return False
            
        if last_completed_at is None:
            return True
            
        seven_days_ago = datetime.now() - timedelta(days=7)
        return last_completed_at < seven_days_ago
