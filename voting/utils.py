import secrets
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from smtplib import SMTPException
from django.conf import settings
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils import timezone

def generate_otp():
    return str(secrets.randbelow(900000) + 100000)



ADMIN_EMAIL = "narisnarendras6@email.com"  # keep your existing value

def send_otp_email(email, otp, user=None):
    subject = "Voting System - OTP Verification"
    message = f"""
Hello,

Your One-Time Password (OTP) is:

{otp}

This OTP is valid for 5 minutes.

If you did not request this, please ignore this email.

Regards,
Campaign Voting System
"""

    # 1) Validate email format
    try:
        validate_email(email)
    except ValidationError:
        # notify admin (but never block user flow)
        try:
            send_mail(
                "🚨 INVALID EMAIL FORMAT DETECTED",
                f"""
User attempted to use an invalid email format.

Username : {getattr(user, "username", "Unknown")}
User ID  : {getattr(user, "id", "Unknown")}
Email    : {email}
Time     : {timezone.now()}
""",
                settings.EMAIL_HOST_USER,
                [ADMIN_EMAIL],
                fail_silently=True,
            )
        except Exception:
            pass
        return False, "Invalid email format"

    # 2) Send OTP (never let it hang too long)
    try:
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )
        return True, None

    except Exception as e:
        # notify admin, but do NOT crash registration
        try:
            send_mail(
                "🚨 OTP EMAIL DELIVERY FAILED",
                f"""
OTP email could not be delivered.

User Details:
-------------
Username : {getattr(user, "username", "Unknown")}
User ID  : {getattr(user, "id", "Unknown")}
Attempted Email : {email}

Time:
-----
{timezone.now()}

SMTP Error:
----------
{str(e)}
""",
                settings.DEFAULT_FROM_EMAIL,
                [ADMIN_EMAIL],
                fail_silently=True,
            )
        except Exception:
            pass

        return False, "OTP sending failed. Please try again later."
