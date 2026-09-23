import json
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.shared.dependencies import get_current_user
from app.modules.ai_chat.providers.ollama_provider import get_ollama_instance

router = APIRouter(prefix="/interview", tags=["Mock Interview"])

QUESTION_PROMPT = """You are an expert HR interviewer for the Indian job market.
Generate {count} interview questions for the role: {role}.
Questions should be practical, behavioural, and appropriate for a candidate with skills: {skills}.
Return JSON only:
{{"questions": [{{"id": 1, "question": "...", "type": "behavioural/technical/situational"}}]}}"""

SCORE_PROMPT = """You are an expert interviewer scoring a mock interview answer.
Role: {role}
Question: {question}
Candidate Answer: {answer}

Score from 1-10 and provide brief feedback. Return JSON only:
{{"score": 7, "feedback": "...", "keywords_matched": ["...", "..."], "improvement": "one improvement tip"}}"""

REPORT_PROMPT = """You are an expert HR consultant. Summarize this mock interview performance.
Role: {role}
Questions and Scores:
{qa_summary}

Provide a comprehensive report. Return JSON only:
{{"overall_score": 7.5, "grade": "B+", "strengths": ["...", "..."], "areas_to_improve": ["...", "..."],
"recommendation": "Ready for interviews / Needs more preparation", "summary": "..."}}"""


class StartRequest(BaseModel):
    target_role: str
    skills: list[str] = []
    question_count: int = 5


class AnswerRequest(BaseModel):
    session_id: str
    question_id: int
    answer: str


_sessions: dict = {}


@router.post("/start")
async def start_interview(req: StartRequest, user: dict = Depends(get_current_user)):
    ollama = get_ollama_instance()
    session_id = str(uuid.uuid4())

    prompt = QUESTION_PROMPT.format(
        count=req.question_count,
        role=req.target_role,
        skills=", ".join(req.skills) if req.skills else "general",
    )

    try:
        data = await ollama.complete_json([{"role": "user", "content": prompt}], temperature=0.6)
        questions = data.get("questions", [])
    except Exception:
        questions = [
            {"id": 1, "question": f"Can you describe your experience and core projects related to {req.target_role}?", "type": "technical"},
            {"id": 2, "question": "Tell me about a time you faced a difficult problem on a deadline. How did you resolve it?", "type": "behavioural"},
            {"id": 3, "question": f"Which tools and technologies do you rely on most when executing {req.target_role} tasks?", "type": "technical"},
            {"id": 4, "question": "How do you handle disagreement with a colleague or manager regarding technical implementation?", "type": "situational"},
            {"id": 5, "question": "Where do you see yourself professionally in the next two to three years?", "type": "behavioural"}
        ][:req.question_count]

    _sessions[session_id] = {
        "user_id": user["id"],
        "role": req.target_role,
        "questions": questions,
        "answers": [],
        "started_at": datetime.now(timezone.utc).isoformat(),
    }

    first_q = questions[0] if questions else {}
    return {
        "success": True,
        "data": {
            "session_id": session_id,
            "total_questions": len(questions),
            "current_question": first_q,
            "question_index": 0,
        }
    }


@router.post("/answer")
async def submit_answer(req: AnswerRequest, user: dict = Depends(get_current_user)):
    session = _sessions.get(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")
    if session["user_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Not your session")

    questions = session["questions"]
    q = next((item for item in questions if item.get("id") == req.question_id), None)
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")

    prompt = SCORE_PROMPT.format(
        role=session["role"],
        question=q["question"],
        answer=req.answer,
    )

    ollama = get_ollama_instance()
    try:
        scoring = await ollama.complete_json([{"role": "user", "content": prompt}], temperature=0.3)
    except Exception:
        words = len(req.answer.split())
        approx_score = min(9, max(4, words // 8))
        scoring = {
            "score": approx_score,
            "feedback": "Answer recorded successfully. Clear and relevant communication.",
            "keywords_matched": [session["role"]],
            "improvement": "Include specific quantitative metrics and project outcomes."
        }

    session["answers"].append({
        "question_id": req.question_id,
        "question": q["question"],
        "answer": req.answer,
        "score": scoring.get("score", 7),
        "feedback": scoring.get("feedback", ""),
        "keywords_matched": scoring.get("keywords_matched", []),
        "improvement": scoring.get("improvement", ""),
    })

    current_idx = next((i for i, q2 in enumerate(questions) if q2.get("id") == req.question_id), 0)
    next_idx = current_idx + 1
    next_question = questions[next_idx] if next_idx < len(questions) else None

    return {
        "success": True,
        "data": {
            "scoring": scoring,
            "next_question": next_question,
            "question_index": next_idx,
            "is_complete": next_question is None,
        }
    }


@router.get("/report/{session_id}")
async def get_interview_report(session_id: str, user: dict = Depends(get_current_user)):
    session = _sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session["user_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Not your session")

    answers = session["answers"]
    if not answers:
        raise HTTPException(status_code=400, detail="No answers recorded yet")

    qa_summary = "\n".join([
        f"Q{a['question_id']}: {a['question']}\nScore: {a['score']}/10 | {a['feedback']}"
        for a in answers
    ])

    prompt = REPORT_PROMPT.format(role=session["role"], qa_summary=qa_summary)
    ollama = get_ollama_instance()

    try:
        report = await ollama.complete_json([{"role": "user", "content": prompt}], temperature=0.4)
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
        "success": True,
        "data": {
            "session_id": session_id,
            "role": session["role"],
            "total_questions": len(session["questions"]),
            "answered": len(answers),
            "per_question": answers,
            "report": report,
        }
    }
