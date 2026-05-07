"""
AI chat router — SSE streaming response, history, and clear.
"""
import json
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.schemas.request.chat import ChatRequest
from app.schemas.response.chat import ChatMessageResponse
from app.modules.ai_chat.service import ChatService
from app.modules.ai_chat.repository import ChatRepository
from app.shared.dependencies import get_db, get_current_user, get_llm_provider
from app.shared.response_models import ok, APIResponse

router = APIRouter(prefix="/chat", tags=["chat"])


def _get_service(
    db=Depends(get_db), 
    provider=Depends(get_llm_provider)
) -> ChatService:
    return ChatService(ChatRepository(db), provider)


@router.post("/message")
async def send_message(
    body: ChatRequest,
    current_user: dict = Depends(get_current_user),
    service: ChatService = Depends(_get_service),
):
    async def generate():
        try:
            async for token in service.stream_message(
                user_id=current_user["id"],
                content=body.content,
                language=body.language,
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


@router.get("/history", response_model=APIResponse[list[ChatMessageResponse]])
async def get_history(
    current_user: dict = Depends(get_current_user),
    service: ChatService = Depends(_get_service),
):
    return ok(data=await service.get_history(current_user["id"]))


@router.delete("/history")
async def clear_history(
    current_user: dict = Depends(get_current_user),
    service: ChatService = Depends(_get_service),
):
    await service.clear_history(current_user["id"])
    return ok(message="Chat history cleared.")
