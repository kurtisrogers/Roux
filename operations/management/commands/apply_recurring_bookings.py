from django.core.management.base import BaseCommand
from operations.services import apply_recurring_bookings


class Command(BaseCommand):
    help = "Create bookings from active recurring patterns for the next 14 days."

    def handle(self, *args, **options):
        created = apply_recurring_bookings()
        self.stdout.write(self.style.SUCCESS(f"Created {created} recurring booking(s)."))
