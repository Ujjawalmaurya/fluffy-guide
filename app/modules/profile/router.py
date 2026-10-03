"""Profile router — GET/PATCH /profile/me, POST /profile/resume, GET /profile/completion-score."""
from fastapi import APIRouter, Depends, UploadFile, File

from app.modules.profile.service import ProfileService
from app.modules.profile.repository import ProfileRepository
from app.modules.profile.schemas import ProfileUpdateIn, BulletRewriteIn, BulletRewriteOut
from app.shared.dependencies import get_db, get_current_user
from app.shared.response_models import ok

router = APIRouter(prefix="/profile", tags=["profile"])


def _get_service(db=Depends(get_db)) -> ProfileService:
    return ProfileService(ProfileRepository(db))


@router.get("/me")
async def get_profile(current_user: dict = Depends(get_current_user), service: ProfileService = Depends(_get_service)):
    return ok(data=service.get_profile(current_user["id"]))


@router.patch("/me")
async def update_profile(
    body: ProfileUpdateIn,
    current_user: dict = Depends(get_current_user),
    service: ProfileService = Depends(_get_service),
):
    updated = service.update_profile(current_user["id"], body)
    return ok(data=updated, message="Profile updated.")


@router.post("/resume")
async def upload_resume(
    resume: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    service: ProfileService = Depends(_get_service),
):
    file_bytes = await resume.read()
    result = await service.upload_resume(
        user_id=current_user["id"],
        filename=resume.filename or "resume.pdf",
        content_type=resume.content_type or "",
        file_bytes=file_bytes,
    )
    return ok(data=result)


@router.get("/completion-score")
async def get_completion(
    current_user: dict = Depends(get_current_user),
    service: ProfileService = Depends(_get_service),
):
    return ok(data=service.get_completion_score(current_user["id"]))


@router.post("/rewrite-bullets", response_model=BulletRewriteOut)
async def rewrite_bullets(
    body: BulletRewriteIn,
    current_user: dict = Depends(get_current_user),
    service: ProfileService = Depends(_get_service),
):
    return await service.rewrite_bullets(current_user["id"], body.bullets)
