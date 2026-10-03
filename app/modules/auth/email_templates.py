"""
email_templates.py — Clean, responsive email templates for SANKALP auth.
"""

def build_otp_email(otp: str, expire_minutes: int = 10) -> tuple[str, str, str]:
    """
    Returns (subject, html_content, text_content) for an OTP verification email.
    Compatible with modern email clients (Gmail, Apple Mail, Outlook).
    """
    subject = f"{otp} is your SANKALP verification code"
    
    text_content = (
        f"SANKALP — SkillBridge AI\n\n"
        f"Your verification code is: {otp}\n\n"
        f"This code will expire in {expire_minutes} minutes.\n"
        f"Security Notice: Do not share this code with anyone. SANKALP staff will never ask for your OTP.\n\n"
        f"If you did not request this code, you can safely ignore this email.\n"
    )
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Verification Code</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f1f5f9; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; -webkit-font-smoothing: antialiased;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #f1f5f9; padding: 32px 16px;">
    <tr>
      <td align="center">
        <table role="presentation" width="100%" style="max-width: 540px; background-color: #ffffff; border-radius: 16px; border: 1px solid #e2e8f0; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);">
          <!-- Top Accent Bar (Tricolor Inspired / Indigo Core) -->
          <tr>
            <td style="height: 6px; background: linear-gradient(90deg, #ff9933 0%, #4f46e5 50%, #138808 100%);"></td>
          </tr>
          
          <!-- Content Body -->
          <tr>
            <td style="padding: 36px 32px;">
              <!-- Badge -->
              <div style="text-align: center; margin-bottom: 20px;">
                <span style="display: inline-block; padding: 6px 14px; background-color: #eef2ff; color: #4338ca; border-radius: 9999px; font-size: 12px; font-weight: 700; letter-spacing: 0.8px; text-transform: uppercase;">
                  🇮🇳 SANKALP &bull; SkillBridge AI
                </span>
              </div>

              <!-- Title -->
              <h1 style="margin: 0 0 8px; font-size: 22px; font-weight: 700; color: #0f172a; text-align: center; letter-spacing: -0.3px;">
                Verification Code
              </h1>
              <p style="margin: 0 0 28px; font-size: 15px; line-height: 1.5; color: #475569; text-align: center;">
                Use the one-time password below to securely access your portal.
              </p>

              <!-- OTP Box -->
              <div style="background-color: #f8fafc; border: 2px dashed #cbd5e1; border-radius: 12px; padding: 24px 16px; text-align: center; margin-bottom: 24px;">
                <div style="font-family: ui-monospace, 'SF Mono', Menlo, Consolas, monospace; font-size: 40px; font-weight: 800; letter-spacing: 12px; color: #1e1b4b; padding-left: 12px;">
                  {otp}
                </div>
                <div style="margin-top: 10px; font-size: 13px; font-weight: 500; color: #64748b;">
                  ⏱️ Valid for {expire_minutes} minutes
                </div>
              </div>

              <!-- Security Callout -->
              <div style="background-color: #fffbeb; border-left: 4px solid #f59e0b; padding: 12px 16px; border-radius: 6px; margin-bottom: 28px;">
                <p style="margin: 0; font-size: 13px; line-height: 1.5; color: #92400e;">
                  <strong>Security Reminder:</strong> Never share this code with anyone. SANKALP administrators will never ask for your verification code.
                </p>
              </div>

              <!-- Footer -->
              <div style="border-top: 1px solid #f1f5f9; padding-top: 20px; text-align: center;">
                <p style="margin: 0 0 4px; font-size: 12px; color: #94a3b8; font-weight: 500;">
                  National Skill Development & Career Identity Initiative
                </p>
                <p style="margin: 0; font-size: 12px; color: #cbd5e1;">
                  If you didn't initiate this request, you can safely ignore this email.
                </p>
              </div>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""

    return subject, html_content, text_content
