import resend
from app.core.config import settings
from app.core.logger import get_logger

log = get_logger(__name__)

class EmailService:
    def __init__(self):
        if not settings.resend_api_key:
            log.warning("RESEND_API_KEY not set. Emails will only be logged.")
        resend.api_key = settings.resend_api_key

    def send_otp(self, email: str, otp: str):
        """
        Sends an OTP email using Resend.
        """
        subject = f"{otp} is your SkillBridge verification code"
        html = f"""
        <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eee; border-radius: 10px;">
            <h2 style="color: #333;">Verification Code</h2>
            <p style="font-size: 16px; color: #555;">Use the following code to sign in to SkillBridge:</p>
            <div style="background: #f4f4f4; padding: 20px; text-align: center; font-size: 32px; font-weight: bold; letter-spacing: 5px; border-radius: 5px; margin: 20px 0;">
                {otp}
            </div>
            <p style="font-size: 14px; color: #888;">This code will expire in 10 minutes. If you didn't request this, you can safely ignore this email.</p>
        </div>
        """
        
        # In dev/testing, if no key, just log it
        if not settings.resend_api_key:
            log.info(f"[MOCK EMAIL] OTP {otp} sent to {email}")
            return

        try:
            params = {
                "from": "SkillBridge <onboarding@resend.dev>", # Default sender for trialing
                "to": [email],
                "subject": subject,
                "html": html,
            }
            resend.Emails.send(params)
            log.info(f"OTP email sent to {email} via Resend")
        except Exception as e:
            log.error(f"Failed to send OTP email: {str(e)}")
            # Don't crash the whole flow if email fails, but log it
            # In a real prod app, you might want to retry or throw.
