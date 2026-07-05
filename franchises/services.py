import logging

from django.conf import settings
from django.core.management import call_command
from django.db import connections

from franchises.context import set_franchise_context
from franchises.db import register_franchise_database
from franchises.models import Franchise, FranchiseDomain

logger = logging.getLogger(__name__)


def get_franchise_stripe_config(franchise: Franchise | None) -> dict:
    if franchise and franchise.stripe_secret_key:
        return {
            "publishable_key": franchise.stripe_publishable_key,
            "secret_key": franchise.stripe_secret_key,
            "webhook_secret": franchise.stripe_webhook_secret,
        }
    return {
        "publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
        "secret_key": settings.STRIPE_SECRET_KEY,
        "webhook_secret": settings.STRIPE_WEBHOOK_SECRET,
    }


def get_franchise_xero_config(franchise: Franchise | None) -> dict:
    if franchise and franchise.xero_client_id:
        return {
            "client_id": franchise.xero_client_id,
            "client_secret": franchise.xero_client_secret,
            "redirect_uri": franchise.xero_redirect_uri or settings.XERO_REDIRECT_URI,
        }
    return {
        "client_id": settings.XERO_CLIENT_ID,
        "client_secret": settings.XERO_CLIENT_SECRET,
        "redirect_uri": settings.XERO_REDIRECT_URI,
    }


def provision_franchise(
    name: str,
    slug: str,
    *,
    contact_email: str = "",
    hostname: str = "",
    database_url: str = "",
    seed: bool = True,
) -> Franchise:
    """Create franchise record, database, run migrations, optional seed."""
    franchise, created = Franchise.objects.get_or_create(
        slug=slug,
        defaults={
            "name": name,
            "contact_email": contact_email,
            "database_url": database_url,
            "status": Franchise.Status.PROVISIONING,
        },
    )
    if not created:
        franchise.name = name
        franchise.contact_email = contact_email
        if database_url:
            franchise.database_url = database_url
        franchise.save()

    if hostname:
        FranchiseDomain.objects.get_or_create(
            franchise=franchise,
            hostname=hostname,
            defaults={"is_primary": True},
        )
    else:
        FranchiseDomain.objects.get_or_create(
            franchise=franchise,
            hostname=f"{slug}.localhost",
            defaults={"is_primary": True},
        )

    alias = register_franchise_database(franchise)
    connection = connections[alias]
    connection.ensure_connection()

    call_command("migrate", database=alias, interactive=False, verbosity=0)

    set_franchise_context(franchise, alias)
    if seed:
        call_command("seed_demo")
    set_franchise_context(franchise, alias)

    franchise.status = Franchise.Status.ACTIVE
    franchise.save(update_fields=["status", "updated_at"])
    logger.info("Provisioned franchise %s on database %s", franchise.slug, alias)
    return franchise
