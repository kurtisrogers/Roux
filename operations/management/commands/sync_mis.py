from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Stub MIS sync — configure WONDE/Arbor API keys in production."

    def handle(self, *args, **options):
        self.stdout.write(
            "MIS sync is a stub. Set WONDE_API_KEY or ARBOR credentials and implement "
            "operations.integrations.mis in your deployment."
        )
