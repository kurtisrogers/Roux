from django.core.management.base import BaseCommand

from franchises.services import provision_franchise


class Command(BaseCommand):
    help = "Provision a new franchise with its own isolated database"

    def add_arguments(self, parser):
        parser.add_argument("name", type=str, help="Franchise display name")
        parser.add_argument("--slug", type=str, required=True, help="URL slug (e.g. acme)")
        parser.add_argument("--email", type=str, default="", help="Contact email")
        parser.add_argument(
            "--hostname",
            type=str,
            default="",
            help="Primary hostname (default: {slug}.localhost)",
        )
        parser.add_argument(
            "--database-url",
            type=str,
            default="",
            help="PostgreSQL URL for production franchise DB",
        )
        parser.add_argument("--no-seed", action="store_true", help="Skip demo data seeding")
        parser.add_argument("--admin-email", type=str, default="", help="Franchise admin email")
        parser.add_argument(
            "--admin-name", type=str, default="", help="Franchise admin display name"
        )

    def handle(self, *args, **options):
        franchise, admin_password = provision_franchise(
            name=options["name"],
            slug=options["slug"],
            contact_email=options["email"],
            hostname=options["hostname"],
            database_url=options["database_url"],
            seed=not options["no_seed"],
            admin_email=options["admin_email"],
            admin_name=options["admin_name"] or options["email"],
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Franchise '{franchise.name}' ready at database '{franchise.database_alias}'"
            )
        )
        domain = franchise.domains.filter(is_primary=True).first()
        if domain:
            self.stdout.write(f"  Access via: http://{domain.hostname}:8000/")
        if admin_password:
            self.stdout.write(self.style.WARNING(f"  Franchise admin password: {admin_password}"))
