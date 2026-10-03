try:
    import resend
except ImportError:
    resend = None

from app.core.config import settings
from app.core.logger import get_logger
from app.modules.auth.email_templates import build_otp_email

log = get_logger(__name__)


class EmailService:
    def __init__(self):
        if resend and settings.resend_api_key:
            resend.api_key = settings.resend_api_key
        else:
            log.warning("Resend library or RESEND_API_KEY missing. Emails will only be logged.")

    def send_otp(self, email: str, otp: str):
        """Sends an OTP email using Resend, or falls back to logger in dev/test."""
        subject, html_content, text_content = build_otp_email(
            otp=otp, 
            expire_minutes=settings.otp_expire_minutes
        )

        if not resend or not settings.resend_api_key:
            log.info(f"[MOCK EMAIL] OTP {otp} sent to {email}")
            return

        try:
            params = {
                "from": settings.resend_from_email,
                "to": [email],
                "subject": subject,
                "html": html_content,
                "text": text_content,
            }
            resend.Emails.send(params)
            log.info(f"OTP email sent to {email} via Resend")
        except Exception as e:
            log.error(f"Failed to send OTP email via Resend: {e}")
            log.info(f"[MOCK EMAIL FALLBACK] OTP {otp} for {email}")
