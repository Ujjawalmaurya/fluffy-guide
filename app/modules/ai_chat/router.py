"""
AI chat router — SSE streaming response, history, and clear.
"""
import json
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.modules.ai_chat.schemas import ChatMessageIn
from app.modules.ai_chat.service import ChatService
from app.modules.ai_chat.repository import ChatRepository
from app.shared.dependencies import get_db, get_current_user
from app.shared.response_models import ok

router = APIRouter(prefix="/chat", tags=["chat"])


def _get_service(db=Depends(get_db)) -> ChatService:
    return ChatService(ChatRepository(db))


def _get_profile(user_id: str, db) -> dict | None:
    result = db.table("user_profiles").select("*").eq("user_id", user_id).execute()
    return result.data[0] if result.data else None


def _get_prefs(user_id: str, db) -> dict | None:
    result = db.table("user_preferences").select("*").eq("user_id", user_id).execute()
    return result.data[0] if result.data else None


@router.post("/message")
async def send_message(
    body: ChatMessageIn,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db),
    service: ChatService = Depends(_get_service),
):
    profile = _get_profile(current_user["id"], db)
    prefs = _get_prefs(current_user["id"], db)

    async def generate():
        try:
            async for token in service.stream_message(
                user_id=current_user["id"],
                content=body.content,
                language=body.language,
                user=current_user,
                profile=profile,
                prefs=prefs,
            ):
                # SSE format
                yield f"data: {json.dumps({'token': token})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            from app.core.logger import get_logger
            log = get_logger("AI_CHAT")
            log.error(f"Streaming failed mid-way: {e}")
            # Send error info to frontend before closing
            yield f"data: {json.dumps({'error': 'AI service is temporarily unavailable.'})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/history")
async def get_history(
    current_user: dict = Depends(get_current_user),
    service: ChatService = Depends(_get_service),
):
    return ok(data=service.get_history(current_user["id"]))


@router.delete("/history")
async def clear_history(
    current_user: dict = Depends(get_current_user),
    service: ChatService = Depends(_get_service),
):
    service.clear_history(current_user["id"])
    return ok(message="Chat history cleared.")
