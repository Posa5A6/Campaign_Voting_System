import secrets
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from smtplib import SMTPException

def generate_otp():
    return str(secrets.randbelow(900000) + 100000)


from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

ADMIN_EMAIL = "narisnarendras6@gmail.com"

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

    # ✅ STEP 1: EMAIL FORMAT VALIDATION
    try:
        validate_email(email)
    except ValidationError:
        send_mail(
            "🚨 INVALID EMAIL FORMAT DETECTED",
            f"""
User attempted to use an invalid email format.

Username : {user.username if user else 'Unknown'}
User ID  : {user.id if user else 'Unknown'}
Email    : {email}
Time     : {timezone.now()}
""",
            settings.EMAIL_HOST_USER,
            [ADMIN_EMAIL],
            fail_silently=True
        )
        raise Exception("Invalid email format")

    # ✅ STEP 2: TRY SMTP DELIVERY
    try:
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

    except Exception as e:
        # ❌ SMTP / NETWORK / AUTH FAILURE

        admin_subject = "🚨 OTP EMAIL DELIVERY FAILED"
        admin_message = f"""
OTP email could not be delivered.

User Details:
-------------
Username : {user.username if user else 'Unknown'}
User ID  : {user.id if user else 'Unknown'}
Attempted Email : {email}

Time:
-----
{timezone.now()}

SMTP Error:
----------
{str(e)}
"""

        send_mail(
            admin_subject,
            admin_message,
            settings.EMAIL_HOST_USER,
            [ADMIN_EMAIL],
            fail_silently=True,
        )

        raise Exception("OTP email delivery failed. Admin notified.")
