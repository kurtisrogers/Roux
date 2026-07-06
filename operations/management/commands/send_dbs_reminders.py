from django.core.management.base import BaseCommand
from notifications.services import notify_dbs_expiry_reminder
from operations.models import StaffCompliance


class Command(BaseCommand):
    help = "Email admins about DBS certificates expiring within 30 days."

    def handle(self, *args, **options):
        from datetime import timedelta

        from django.utils import timezone

        soon = timezone.now().date() + timedelta(days=30)
        count = 0
        for record in StaffCompliance.objects.filter(
            dbs_expiry__lte=soon,
            dbs_expiry__gte=timezone.now().date(),
        ):
            notify_dbs_expiry_reminder(record)
            count += 1
        self.stdout.write(self.style.SUCCESS(f"Sent {count} DBS reminder(s)."))
