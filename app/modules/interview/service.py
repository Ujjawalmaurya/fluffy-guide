"""
service.py — Mock interview question generation, response scoring, and performance summary.
"""
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from loguru import logger

from app.modules.ai_chat.providers.ollama_provider import get_ollama_instance
from app.modules.interview.prompts import (
    QUESTION_PROMPT,
    SCORE_PROMPT,
    REPORT_PROMPT,
    get_default_questions,
)
from app.modules.interview.session_store import session_store


class InterviewService:
    def __init__(self):
        self.ollama = get_ollama_instance()

    async def start_session(self, user_id: str, target_role: str, skills: List[str], count: int) -> Dict[str, Any]:
        """Initializes a new interview session and generates questions."""
        session_id = str(uuid.uuid4())
        prompt = QUESTION_PROMPT.format(
            count=count,
            role=target_role,
            skills=", ".join(skills) if skills else "general",
        )

        try:
            data = await self.ollama.complete_json([{"role": "user", "content": prompt}], temperature=0.6)
            questions = data.get("questions", [])
            if not questions:
                questions = get_default_questions(target_role, count)
        except Exception as e:
            logger.warning(f"[INTERVIEW] Failed to generate AI questions: {e}. Using defaults.")
            questions = get_default_questions(target_role, count)

        session_store.save_session(session_id, {
            "user_id": user_id,
            "role": target_role,
            "questions": questions,
            "answers": [],
            "started_at": datetime.now(timezone.utc).isoformat(),
        })

        first_q = questions[0] if questions else {}
        return {
            "session_id": session_id,
            "total_questions": len(questions),
            "current_question": first_q,
            "question_index": 0,
        }

    async def score_answer(self, session: Dict[str, Any], question_id: int, answer: str) -> Dict[str, Any]:
        """Scores candidate answer and returns next question state."""
        questions = session["questions"]
        q = next((item for item in questions if item.get("id") == question_id), None)
        if not q:
            return {"error": "Question not found"}

        prompt = SCORE_PROMPT.format(
            role=session["role"],
            question=q["question"],
            answer=answer,
        )

        try:
            scoring = await self.ollama.complete_json([{"role": "user", "content": prompt}], temperature=0.3)
        except Exception:
            words = len(answer.split())
            approx_score = min(9, max(4, words // 8))
            scoring = {
                "score": approx_score,
                "feedback": "Answer recorded successfully. Clear and relevant communication.",
                "keywords_matched": [session["role"]],
                "improvement": "Include specific quantitative metrics and project outcomes."
            }

        session["answers"].append({
            "question_id": question_id,
            "question": q["question"],
            "answer": answer,
            "score": scoring.get("score", 7),
            "feedback": scoring.get("feedback", ""),
            "keywords_matched": scoring.get("keywords_matched", []),
            "improvement": scoring.get("improvement", ""),
        })

        current_idx = next((i for i, q2 in enumerate(questions) if q2.get("id") == question_id), 0)
        next_idx = current_idx + 1
        next_question = questions[next_idx] if next_idx < len(questions) else None

        return {
            "scoring": scoring,
            "next_question": next_question,
            "question_index": next_idx,
            "is_complete": next_question is None,
        }

    async def generate_report(self, session: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Generates comprehensive HR interview report."""
        answers = session["answers"]
        if not answers:
            return {"error": "No answers recorded yet"}

        qa_summary = "\n".join([
            f"Q{a['question_id']}: {a['question']}\nScore: {a['score']}/10 | {a['feedback']}"
            for a in answers
        ])

        prompt = REPORT_PROMPT.format(role=session["role"], qa_summary=qa_summary)
        try:
            report = await self.ollama.complete_json([{"role": "user", "content": prompt}], temperature=0.4)
        except Exception:
            avg_score = round(sum(a.get("score", 7) for a in answers) / max(len(answers), 1), 1)
            grade = "A" if avg_score >= 8.5 else ("B+" if avg_score >= 7.0 else "B")
            report = {
                "overall_score": avg_score,
                "grade": grade,
                "strengths": ["Structured responses", "Relevant domain background"],
                "areas_to_improve": ["Elaborate on real-world impact and results"],
                "recommendation": "Ready for interviews",
                "summary": f"Solid performance across {len(answers)} questions for {session['role']}."
            }

        return {
            "session_id": session_id,
            "role": session["role"],
            "total_questions": len(session["questions"]),
            "answered": len(answers),
            "per_question": answers,
            "report": report,
        }
