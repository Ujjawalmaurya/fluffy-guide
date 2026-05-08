"""
Custom exception classes and global exception handlers.
All errors use the standard {success, error_code, message, details} format.
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from app.core.config import settings
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
        log.warning("AppError [{}]: {}", exc.error_code, exc.message)
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
        errors = exc.errors()
        log.warning("Validation error: {}", errors)
        
        # Comprehensive field mapping for human-readable labels
        FIELD_MAP = {
            "full_name": "Full Name",
            "age": "Age",
            "gender": "Gender",
            "state": "State",
            "city": "City",
            "preferred_job_location": "Preferred Location",
            "education_level": "Education Level",
            "stream": "Stream / Branch",
            "institution_name": "Institution Name",
            "career_interests": "Career Interests",
            "languages_known": "Languages",
            "primary_trade": "Primary Trade / Skill",
            "years_experience": "Years of Experience",
            "current_work_type": "Current Work Type",
            "monthly_income": "Monthly Income",
            "digital_literacy": "Digital Literacy Level",
            "contact_person_name": "Contact Person Name",
            "designation": "Designation",
            "company_name": "Company Name",
            "industry_sector": "Industry Sector",
            "org_name": "Organization Name",
            "registration_number": "Registration Number",
            "focus_sectors": "Focus Sectors",
            "coverage_areas": "Coverage Areas",
            "department": "Department",
            "access_level": "Access Level",
            "state_jurisdiction": "State Jurisdiction",
            "otp": "OTP Code",
            "email": "Email Address",
            "content": "Message",
            "resume_text": "Resume Content",
            "village_district": "Village / District",
            "secondary_skills": "Secondary Skills",
            "is_currently_employed": "Employment Status",
            "preferred_work_radius": "Work Radius",
            "owns_smartphone": "Smartphone Ownership",
            "city_village": "City / Village",
            "interests": "Interests",
            "company_size": "Company Size",
            "roles_hiring_for": "Roles Hiring For",
            "preferred_skills": "Preferred Skills",
            "work_type_offered": "Work Type Offered",
            "beneficiary_types": "Beneficiary Types",
            "contact_name": "Contact Name",
            "contact_designation": "Contact Designation",
            "district_jurisdiction": "District Jurisdiction",
            "user_type": "User Type",
            "question_id": "Question ID",
            "answer": "Answer",
            "answers": "Answers",
            "career_goal": "Career Goal",
            "career_stage": "Career Stage",
            "timeframe_months": "Timeframe (Months)",
            "timeframe_weeks": "Timeframe (Weeks)",
            "expected_salary_min": "Min Expected Salary",
            "expected_salary_max": "Max Expected Salary",
            "job_type": "Job Type",
            "work_type": "Preferred Work Type",
            "work_mode": "Work Mode",
            "willing_to_relocate": "Willing to Relocate",
            "target_roles": "Target Roles",
            "target_role": "Target Role",
            "target_job_id": "Target Job",
            "preferred_lang": "Preferred Language",
            "skill_tags": "Skill Tags",
            "skills": "Skills",
            "interests": "Interests",
            "domain": "Domain",
            "category": "Category",
            "difficulty_level": "Difficulty Level",
            "duration_weeks": "Duration (Weeks)",
            "is_free": "Is Free?",
            "is_active": "Is Active?",
            "cost_inr": "Cost (INR)",
            "delivery_type": "Delivery Type",
            "provider": "Provider",
            "url": "URL",
            "location": "Location",
            "location_state": "Location State",
            "location_city": "Location City",
            "salary_min": "Min Salary",
            "salary_max": "Max Salary",
            "experience_min": "Min Experience",
            "required_skills": "Required Skills",
            "source_url": "Source URL",
            "company": "Company",
            "role": "Role",
            "limit": "Limit",
            "page": "Page",
            "query": "Search Query",
            "personal_info": "Personal Info",
            "primary_role": "Primary Role",
            "total_experience_years": "Total Experience (Years)",
            "degree": "Degree",
            "institution": "Institution",
            "year_range": "Year Range",
            "coursework": "Coursework",
            "responsibilities": "Responsibilities",
            "technologies": "Technologies",
            "proficiency": "Proficiency",
            "summary": "Summary",
            "strengths": "Strengths",
            "weaknesses": "Weaknesses",
            "career_suggestions": "Career Suggestions",
            "skill_gap_analysis": "Skill Gap Analysis",
            "total_weeks": "Total Weeks",
            "weekly_commitment_hours": "Weekly Commitment (Hours)",
            "milestone": "Milestone",
            "motivational_note": "Motivational Note",
            "work_type_offered": "Offered Work Type",
        }

        msg = "Request validation failed."
        if errors:
            first_err = errors[0]
            loc = first_err.get("loc", [])
            # Skip 'body' or 'query' prefix in location
            field_parts = [str(p) for p in loc if p not in ("body", "query", "path")]
            field = field_parts[-1] if field_parts else "field"
            
            # Use map if exists, else format the raw field name
            field_label = FIELD_MAP.get(field, field.replace('_', ' ').title())
            
            error_type = first_err.get("type", "")
            raw_input = first_err.get("input")
            
            # Custom messages for common validation failures
            if error_type == "missing":
                msg = f"'{field_label}' is required. Please provide a value."
            elif "enum" in error_type:
                expected = first_err.get('ctx', {}).get('expected', '')
                if raw_input == "" or raw_input is None:
                    msg = f"Please select a valid '{field_label}' from the options."
                else:
                    msg = f"'{raw_input}' is not a valid choice for '{field_label}'."
                
                if expected:
                    # Clean up the expected choices list
                    options = [o.strip("'") for o in expected.split(", ")]
                    if len(options) <= 12:
                        msg += f" Allowed: {', '.join(options)}."
                    else:
                        msg += " Please choose a valid option from the dropdown."
            elif error_type == "string_too_short":
                min_len = first_err.get('ctx', {}).get('min_length', '?')
                msg = f"'{field_label}' is too short. It must be at least {min_len} characters."
            elif error_type == "string_too_long":
                max_len = first_err.get('ctx', {}).get('max_length', '?')
                msg = f"'{field_label}' is too long. Maximum {max_len} characters allowed."
            elif error_type == "email_type":
                msg = f"Please enter a valid email address."
            elif error_type == "greater_than_equal":
                ge = first_err.get('ctx', {}).get('ge', '?')
                msg = f"'{field_label}' must be at least {ge}."
            elif error_type == "less_than_equal":
                le = first_err.get('ctx', {}).get('le', '?')
                msg = f"'{field_label}' must be at most {le}."
            elif error_type == "int_parsing":
                msg = f"'{field_label}' must be a valid number."
            elif "parsing" in error_type:
                msg = f"Invalid format for '{field_label}'."
            else:
                # Fallback to the provided message but made slightly more readable
                err_msg = first_err.get("msg", "Invalid value")
                if err_msg.startswith("Value error, "):
                    err_msg = err_msg[len("Value error, "):]
                msg = f"Problem with '{field_label}': {err_msg}"
            
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error_code": "VALIDATION_ERROR",
                "message": msg,
                "details": {"errors": errors},
            }
        )

    @app.exception_handler(ValidationError)
    async def pydantic_validation_error_handler(request: Request, exc: ValidationError):
        """Handle Pydantic internal validation errors (e.g. from service layer)."""
        errors = exc.errors()
        log.error("Internal Data Integrity Error: {}", errors)
        
        msg = "We encountered an internal data error. This has been logged."
        if settings.app_env == "development":
            msg = f"Data Error: {errors[0].get('msg', 'Invalid state')}"
            
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error_code": "INTERNAL_VALIDATION_ERROR",
                "message": msg,
                "details": {"errors": errors} if settings.app_env == "development" else {},
            }
        )

    @app.exception_handler(Exception)
    async def generic_error_handler(request: Request, exc: Exception):
        log.error("Unhandled exception: {}: {}", type(exc).__name__, str(exc), exc_info=True)
        
        msg = "Something went wrong on our end."
        error_type = type(exc).__name__
        
        if settings.app_env == "development":
            # Make it LOUD for developers
            msg = f"SERVER_CRASH [{error_type}]: {str(exc)}"
            
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error_code": "SERVER_ERROR",
                "message": msg,
                "details": {
                    "type": error_type,
                    "exception": str(exc)
                } if settings.app_env == "development" else {},
            }
        )


# Convenience — pre-built errors for each error code
class Conflict(AppError):
    def __init__(self, message="Conflict"): super().__init__("CONFLICT", message, 409)

class UserNotFound(AppError):
    def __init__(self, message="User not found."): super().__init__("USER_NOT_FOUND", message, 404)

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

class GapAnalysisNoSkills(AppError):
    def __init__(self): super().__init__("GAP_ANALYSIS_NO_SKILLS", "Complete your assessment or upload a resume first. We need to know your skills before analyzing gaps.", 400)
    # log_level: INFO

class GapAnalysisNoJobs(AppError):
    def __init__(self): super().__init__("GAP_ANALYSIS_NO_JOBS", "No job listings available for your region yet. We are adding more regularly. Please check back soon.", 404)
    # log_level: INFO
