import os
import secrets
import requests
import logging
from django.utils import timezone
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)

ADMIN_EMAIL = "narisnarendras6@gmail.com"

def generate_otp() -> str:
    return str(secrets.randbelow(900000) + 100000)

def send_otp_email(email: str, otp: str, user=None):
    # validate email
    try:
        validate_email(email)
    except ValidationError:
        return False, "Invalid email format"

    api_key = os.environ.get("BREVO_API_KEY")
    sender_email = os.environ.get("DEFAULT_FROM_EMAIL", ADMIN_EMAIL)
    sender_name = os.environ.get("SENDER_NAME", "Campaign Voting System")

    if not api_key:
        logger.error("BREVO_API_KEY is missing")
        return False, "Email service not configured"

    subject = "Voting System - OTP Verification"
    html_content = f"""
    <p>Hello,</p>
    <p>Your One-Time Password (OTP) is:</p>
    <h2>{otp}</h2>
    <p>This OTP is valid for <b>5 minutes</b>.</p>
    <p>If you did not request this, please ignore this email.</p>
    <p>Regards,<br/>Campaign Voting System</p>
    """

    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "content-type": "application/json",
    }
    payload = {
        "sender": {"name": sender_name, "email": sender_email},
        "to": [{"email": email}],
        "subject": subject,
        "htmlContent": html_content,
    }

    try:
        r = requests.post(url, json=payload, headers=headers, timeout=15)
        if r.status_code in (200, 201, 202):
            logger.info("✅ OTP sent via Brevo API to %s at %s", email, timezone.now())
            return True, None

        logger.error("Brevo API failed: status=%s body=%s", r.status_code, r.text)
        return False, "OTP sending failed (email provider error)"

    except Exception as e:
        logger.exception("Brevo API exception: %r", e)
        return False, "OTP sending failed (network error)"
