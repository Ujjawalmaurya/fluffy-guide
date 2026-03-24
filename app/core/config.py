"""
Backend config — reads all settings from .env via Pydantic BaseSettings.
Single source of truth for env vars. Import `settings` everywhere.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


from app.core.ai_models import AIModel


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Supabase
    supabase_url: str
    supabase_service_key: str
    supabase_anon_key: str

    # Resend
    resend_api_key: str = ""

    # JWT
    jwt_secret_key: str

    # SarvamAI
    sarvam_api_key: str

    # Admin
    admin_secret: str
    demo_password: str = "12345678"

    # App
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "DEBUG"
    cors_origins: str = "http://localhost:5173"

    # API Keys
    openai_api_key: str = ""
    gemini_api_key: str = ""
    groq_api_key: str = ""

    # ── Hardcoded config below ──────────
    @property
    def jwt_algorithm(self) -> str: return "HS256"
    @property
    def jwt_access_expire_minutes(self) -> int: return 30
    @property
    def jwt_refresh_expire_days(self) -> int: return 7

    @property
    def otp_expire_minutes(self) -> int: return 10
    @property
    def otp_length(self) -> int: return 6

    @property
    def sarvam_base_url(self) -> str: return "https://api.sarvam.ai/v1"
    @property
    def sarvam_model(self) -> str: return "sarvam-m"

    @property
    def openai_model(self) -> str: return AIModel.GPT_4O_MINI
    @property
    def openai_max_retries(self) -> int: return 3
    @property
    def openai_rpm_limit(self) -> int: return 3

    @property
    def gemini_model(self) -> str: return AIModel.GEMINI_1_5_FLASH
    @property
    def gemini_max_retries(self) -> int: return 3
    @property
    def gemini_rpm_limit(self) -> int: return 12

    @property
    def groq_model(self) -> str: return AIModel.LLAMA_3_3_70B

    @property
    def assessment_max_questions(self) -> int: return 11
    @property
    def assessment_min_questions(self) -> int: return 9
    @property
    def assessment_max_retakes(self) -> int: return 2
    @property
    def assessment_retake_cooldown_hours(self) -> int: return 24

    @property
    def resume_analysis_max_file_size_mb(self) -> int: return 5
    @property
    def resume_bullet_daily_limit(self) -> int: return 10

    # Derived — parsed from cors_origins string
    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]


# Single shared instance — import this, not the class
settings = Settings()
