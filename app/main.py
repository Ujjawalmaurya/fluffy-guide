"""
main.py — app factory. Mounts all routers, registers exception handlers,
runs startup checks. This is the only file that knows about all modules.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import test_connection
from app.core.logger import get_logger
from app.shared.exceptions import register_exception_handlers

from app.modules.auth.router import router as auth_router
from app.modules.onboarding.router import router as onboarding_router
from app.modules.profile.router import router as profile_router
from app.modules.dashboard.router import router as dashboard_router
from app.modules.jobs.router import router as jobs_router
from app.modules.ai_chat.router import router as chat_router

log = get_logger("MAIN")

app = FastAPI(
    title="SkillBridge AI",
    description="AI-powered career guidance for India's workforce",
    version="1.0.0",
)

# CORS — frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handlers
register_exception_handlers(app)

# Mount all routers
app.include_router(auth_router)
app.include_router(onboarding_router)
app.include_router(profile_router)
app.include_router(dashboard_router)
app.include_router(jobs_router)
app.include_router(chat_router)


@app.on_event("startup")
async def startup():
    log.info(f"SkillBridge AI starting — env={settings.app_env}")
    ok = test_connection()
    if not ok:
        log.error("Supabase connection failed on startup — check .env")
    else:
        log.info("All systems go. Ready to serve requests.")


@app.get("/health")
async def health():
    return {"status": "ok", "env": settings.app_env}
