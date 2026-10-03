"""
router.py — FastAPI endpoints for AI mock interview sessions.
Prefix: /interview
"""
from fastapi import APIRouter, Depends, HTTPException

from app.shared.dependencies import get_current_user
from app.modules.interview.schemas import StartRequest, AnswerRequest
from app.modules.interview.service import InterviewService
from app.modules.interview.session_store import session_store

router = APIRouter(prefix="/interview", tags=["Mock Interview"])
service = InterviewService()


@router.post("/start")
async def start_interview(req: StartRequest, user: dict = Depends(get_current_user)):
    data = await service.start_session(
        user_id=user["id"],
        target_role=req.target_role,
        skills=req.skills,
        count=req.question_count,
    )
    return {"success": True, "data": data}


@router.post("/answer")
async def submit_answer(req: AnswerRequest, user: dict = Depends(get_current_user)):
    session = session_store.get_session(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")
    if session["user_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Not your session")

    data = await service.score_answer(session, req.question_id, req.answer)
    if "error" in data:
        raise HTTPException(status_code=404, detail=data["error"])

    return {"success": True, "data": data}


@router.get("/report/{session_id}")
async def get_interview_report(session_id: str, user: dict = Depends(get_current_user)):
    session = session_store.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session["user_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Not your session")

    data = await service.generate_report(session, session_id)
    if "error" in data:
        raise HTTPException(status_code=400, detail=data["error"])

    return {"success": True, "data": data}
