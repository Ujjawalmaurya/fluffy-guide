"""
Custom exception classes and global exception handlers.
All errors use the standard {success, error_code, message, details} format.
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from app.core.logger import get_logger

log = get_logger("EXCEPTIONS")


class AppError(Exception):
    """Base for all application-level errors."""
    def __init__(self, error_code: str, message: str, status_code: int = 400, details: dict = None):
        self.error_code = error_code
        self.message = message
        self.status_code = status_code
        self.details = details or {}


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        log.warning(f"AppError [{exc.error_code}]: {exc.message}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error_code": exc.error_code,
                "message": exc.message,
                "details": exc.details,
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        log.warning(f"Validation error: {exc.errors()}")
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error_code": "VALIDATION_ERROR",
                "message": "Request validation failed.",
                "details": {"errors": exc.errors()},
            }
        )

    @app.exception_handler(Exception)
    async def generic_error_handler(request: Request, exc: Exception):
        log.error(f"Unhandled exception: {type(exc).__name__}: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error_code": "SERVER_ERROR",
                "message": "Something went wrong on our end.",
                "details": {},
            }
        )


# Convenience — pre-built errors for each error code
class OTPNotFound(AppError):
    def __init__(self): super().__init__("AUTH_OTP_NOT_FOUND", "No OTP found for this email. Request a new one.", 404)

class OTPExpired(AppError):
    def __init__(self): super().__init__("AUTH_OTP_EXPIRED", "Your OTP has expired. Please request a new one.", 400)

class OTPAlreadyUsed(AppError):
    def __init__(self): super().__init__("AUTH_OTP_ALREADY_USED", "This OTP has already been used.", 400)

class OTPInvalid(AppError):
    def __init__(self): super().__init__("AUTH_OTP_INVALID", "Incorrect OTP. Please try again.", 400)

class TokenExpired(AppError):
    def __init__(self): super().__init__("AUTH_TOKEN_EXPIRED", "Your session has expired. Please log in again.", 401)

class TokenInvalid(AppError):
    def __init__(self): super().__init__("AUTH_TOKEN_INVALID", "Invalid token.", 401)

class Unauthorized(AppError):
    def __init__(self): super().__init__("AUTH_UNAUTHORIZED", "Unauthorized.", 401)

class OnboardingStepIncomplete(AppError):
    def __init__(self, msg="Complete previous steps first."): super().__init__("ONBOARDING_STEP_INCOMPLETE", msg, 400)

class ResumeInvalid(AppError):
    def __init__(self): super().__init__("PROFILE_RESUME_INVALID", "Only PDF files are accepted.", 400)

class ResumeTooLarge(AppError):
    def __init__(self): super().__init__("PROFILE_RESUME_TOO_LARGE", "Resume must be under 5MB.", 400)

class AIProviderUnavailable(AppError):
    def __init__(self): super().__init__("AI_PROVIDER_UNAVAILABLE", "AI service is temporarily unavailable.", 503)

class AIResponseParseError(AppError):
    def __init__(self): super().__init__("AI_RESPONSE_PARSE_ERROR", "Could not parse AI response. Try again.", 502)

class JobNotFound(AppError):
    def __init__(self): super().__init__("JOBS_NOT_FOUND", "Job not found.", 404)

class AdminUnauthorized(AppError):
    def __init__(self): super().__init__("ADMIN_UNAUTHORIZED", "Invalid admin secret.", 403)

class ResumeNoText(AppError):
    def __init__(self): super().__init__("RESUME_NO_TEXT", "Your PDF appears to be a scanned image. Please upload a text-based PDF or try a different file.", 400)
    # log_level: WARNING

class ResumeGeminiFailed(AppError):
    def __init__(self): super().__init__("RESUME_GEMINI_FAILED", "We could not process your resume right now. Please try again in a moment.", 500)
    # log_level: ERROR

class GeminiRateLimit(AppError):
    def __init__(self): super().__init__("GEMINI_RATE_LIMIT", "Analysis is taking a moment longer. Please wait...", 429)
    # log_level: WARNING

class GeminiParseError(AppError):
    def __init__(self): super().__init__("GEMINI_PARSE_ERROR", "We encountered an issue processing your data. Please try again.", 422)
    # log_level: ERROR

class OpenAIRateLimit(AppError):
    def __init__(self): super().__init__("OPENAI_RATE_LIMIT", "Your assessment is paused briefly. Resuming automatically...", 429)
    # log_level: WARNING

class OpenAIQuotaExceeded(AppError):
    def __init__(self): super().__init__("OPENAI_QUOTA_EXCEEDED", "Assessment service is temporarily unavailable. Please try again in a few hours.", 503)
    # log_level: ERROR (CRITICAL)

class GroqRateLimit(AppError):
    def __init__(self): super().__init__("GROQ_RATE_LIMIT", "We are processing too many requests. Please wait a moment.", 429)

class GroqFailed(AppError):
    def __init__(self): super().__init__("GROQ_FAILED", "The AI rewriter is temporarily unavailable.", 503)

class GapAnalysisNoSkills(AppError):
    def __init__(self): super().__init__("GAP_ANALYSIS_NO_SKILLS", "Complete your assessment or upload a resume first. We need to know your skills before analyzing gaps.", 400)
    # log_level: INFO

class GapAnalysisNoJobs(AppError):
    def __init__(self): super().__init__("GAP_ANALYSIS_NO_JOBS", "No job listings available for your region yet. We are adding more regularly. Please check back soon.", 404)
    # log_level: INFO

class RateLimitExceeded(AppError):
    def __init__(self, msg="Daily limit reached."): super().__init__("RATE_LIMIT_EXCEEDED", msg, 429)
