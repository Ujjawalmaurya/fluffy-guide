"""
interview/router.py — Mock Interview endpoints
POST /interview/start  → creates a session, returns first question
POST /interview/answer → scores answer, saves it, returns next question
GET  /interview/report → aggregates all answers into a final report
"""
import json
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from groq import Groq
import os

from app.shared.dependencies import get_current_user, get_db
from supabase import Client

router = APIRouter(prefix="/interview", tags=["Mock Interview"])

def _groq() -> Groq:
    key = os.getenv("GROQ_API_KEY", "")
    if not key:
        raise HTTPException(status_code=503, detail="GROQ_API_KEY not set")
    return Groq(api_key=key)


QUESTION_PROMPT = """You are an expert HR interviewer for Indian job market.
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


# In-memory session store (suitable for hackathon demo)
_sessions: dict = {}


@router.post("/start")
async def start_interview(req: StartRequest, user: dict = Depends(get_current_user)):
    client = _groq()
    session_id = str(uuid.uuid4())
    
    # Generate questions
    prompt = QUESTION_PROMPT.format(
        count=req.question_count,
        role=req.target_role,
        skills=", ".join(req.skills) if req.skills else "general",
    )
    raw = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=512,
        temperature=0.8,
    ).choices[0].message.content.strip()
    
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"): raw = raw[4:]
    
    questions = json.loads(raw).get("questions", [])
    
    _sessions[session_id] = {
        "user_id": user["id"],
        "role": req.target_role,
        "questions": questions,
        "answers": [],
        "started_at": datetime.utcnow().isoformat(),
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
    
    client = _groq()
    questions = session["questions"]
    
    # Find the question
    q = next((q for q in questions if q.get("id") == req.question_id), None)
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Score the answer
    prompt = SCORE_PROMPT.format(
        role=session["role"],
        question=q["question"],
        answer=req.answer,
    )
    raw = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=256,
        temperature=0.5,
    ).choices[0].message.content.strip()
    
    try:
        if "{" in raw and "}" in raw:
            json_str = raw[raw.find("{"):raw.rfind("}")+1]
            scoring = json.loads(json_str)
        else:
            scoring = {"score": 5, "feedback": "Could not parse scoring.", "keywords_matched": [], "improvement": ""}
    except Exception as e:
        scoring = {"score": 5, "feedback": f"Error parsing scoring: {str(e)}", "keywords_matched": [], "improvement": ""}
        
    session["answers"].append({
        "question_id": req.question_id,
        "question": q["question"],
        "answer": req.answer,
        "score": scoring.get("score", 5),
        "feedback": scoring.get("feedback", ""),
        "keywords_matched": scoring.get("keywords_matched", []),
        "improvement": scoring.get("improvement", ""),
    })
    
    # Return next question if available
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
    
    client = _groq()
    qa_summary = "\n".join([
        f"Q{a['question_id']}: {a['question']}\nScore: {a['score']}/10 | {a['feedback']}"
        for a in answers
    ])
    
    prompt = REPORT_PROMPT.format(role=session["role"], qa_summary=qa_summary)
    raw = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400,
        temperature=0.6,
    ).choices[0].message.content.strip()
    
    try:
        if "{" in raw and "}" in raw:
            json_str = raw[raw.find("{"):raw.rfind("}")+1]
            report = json.loads(json_str)
        else:
            report = {"overall_score": 5, "grade": "C", "strengths": [], "areas_to_improve": [], "recommendation": "Needs more preparation", "summary": "Could not parse report."}
    except Exception as e:
        report = {"overall_score": 5, "grade": "C", "strengths": [], "areas_to_improve": [], "recommendation": "Needs more preparation", "summary": f"Error parsing report: {str(e)}"}
    
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
