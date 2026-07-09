"""
Backend config — reads all settings from .env via Pydantic BaseSettings.
Single source of truth for env vars. Import `settings` everywhere.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Supabase
    supabase_url: str
    supabase_service_key: str

    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_expire_minutes: int = 360
    jwt_refresh_expire_days: int = 7

    # OTP
    otp_expire_minutes: int = 10
    otp_length: int = 6

    # SarvamAI
    sarvam_api_key: str
    sarvam_base_url: str = "https://api.sarvam.ai/v1"

    # Admin
    admin_secret: str

    # App
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "DEBUG"
    cors_origins: str = "http://localhost:5173"

    # Ollama
    ollama_host: str = "http://localhost:11434"

    # Assessment
    assessment_max_questions: int = 11
    assessment_min_questions: int = 9
    assessment_max_retakes: int = 2
    assessment_retake_cooldown_hours: int = 24

    # Resume Analysis
    resume_analysis_max_file_size_mb: int = 5
    resume_bullet_daily_limit: int = 10

    # Derived — parsed from cors_origins string
    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]


# Single shared instance — import this, not the class
settings = Settings()
