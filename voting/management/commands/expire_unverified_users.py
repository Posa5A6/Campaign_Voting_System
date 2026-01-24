from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from voting.models import EmailOTP
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = "Delete users who did not verify email within 24 hours"

    def handle(self, *args, **kwargs):
        expiry_time = timezone.now() - timedelta(hours=24)

        records = EmailOTP.objects.filter(
            is_verified=False,
            created_at__lt=expiry_time
        )

        for record in records:
            user = record.user
            user.delete()

        self.stdout.write("Expired unverified users cleaned")
