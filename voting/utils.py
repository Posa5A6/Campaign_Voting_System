import secrets
import logging

from django.conf import settings
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils import timezone

logger = logging.getLogger(__name__)

# ✅ Set your admin email correctly (your real email)
ADMIN_EMAIL = "narisnarendras6@gmail.com"


def generate_otp() -> str:
    """Return 6-digit OTP as string."""
    return str(secrets.randbelow(900000) + 100000)


def send_otp_email(email: str, otp: str, user=None):
    """
    Sends OTP email to user. Returns (True, None) on success.
    Returns (False, "reason") on failure.
    Never raises to avoid 500 errors in production.
    """

    subject = "Voting System - OTP Verification"
    message = (
        "Hello,\n\n"
        "Your One-Time Password (OTP) is:\n\n"
        f"{otp}\n\n"
        "This OTP is valid for 5 minutes.\n\n"
        "If you did not request this, please ignore this email.\n\n"
        "Regards,\n"
        "Campaign Voting System\n"
    )

    # 1) Validate email format
    try:
        validate_email(email)
    except ValidationError:
        # Inform admin silently (optional)
        try:
            send_mail(
                "INVALID EMAIL FORMAT DETECTED",
                (
                    "User attempted to use an invalid email format.\n\n"
                    f"Username : {getattr(user, 'username', 'Unknown')}\n"
                    f"User ID  : {getattr(user, 'id', 'Unknown')}\n"
                    f"Email    : {email}\n"
                    f"Time     : {timezone.now()}\n"
                ),
                settings.DEFAULT_FROM_EMAIL,
                [ADMIN_EMAIL],
                fail_silently=True,
            )
        except Exception:
            pass

        return False, "Invalid email format"

    # 2) Send OTP
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None) or settings.EMAIL_HOST_USER

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,   # ✅ important for Brevo (verified sender)
            recipient_list=[email],
            fail_silently=False,
        )
        logger.info("OTP email sent to %s at %s", email, timezone.now())
        return True, None

    except Exception as e:
        # Log the real error (so you can see it in Render logs)
        logger.exception("OTP EMAIL FAILED for %s. Error=%r", email, e)

        # Notify admin (optional, and must be silent to avoid loop)
        try:
            send_mail(
                "OTP EMAIL DELIVERY FAILED",
                (
                    "OTP email could not be delivered.\n\n"
                    "User Details:\n"
                    "-------------\n"
                    f"Username : {getattr(user, 'username', 'Unknown')}\n"
                    f"User ID  : {getattr(user, 'id', 'Unknown')}\n"
                    f"Attempted Email : {email}\n\n"
                    f"Time: {timezone.now()}\n\n"
                    f"Error: {repr(e)}\n"
                ),
                from_email,
                [ADMIN_EMAIL],
                fail_silently=True,
            )
        except Exception:
            pass

        return False, "OTP sending failed. Please try again later."
