from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from bookings.models import Session
from notifications.services import notify_staff_session_reminder


class Command(BaseCommand):
    help = "Send email reminders to staff assigned to tomorrow's sessions"

    def handle(self, *args, **options):
        tomorrow = timezone.now().date() + timedelta(days=1)
        sessions = Session.objects.filter(
            date=tomorrow,
            status=Session.Status.SCHEDULED,
        ).prefetch_related("staff")
        total = 0
        for session in sessions:
            total += notify_staff_session_reminder(session)
        self.stdout.write(self.style.SUCCESS(f"Sent {total} staff reminder(s) for {sessions.count()} session(s)."))
