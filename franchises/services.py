import logging
import secrets

from accounts.models import User
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


def create_franchise_admin_user(
    franchise: Franchise,
    *,
    email: str,
    name: str,
    password: str | None = None,
) -> tuple[User, str]:
    """Create a Franchise Admin user in the franchise tenant database."""
    if not password:
        password = secrets.token_urlsafe(12)

    parts = name.strip().split(maxsplit=1)
    first_name = parts[0] if parts else ""
    last_name = parts[1] if len(parts) > 1 else ""

    base_username = email.split("@")[0].replace(".", "_")[:30] or f"admin_{franchise.slug}"
    username = base_username
    counter = 1

    alias = franchise.database_alias
    set_franchise_context(franchise, alias)
    while User.objects.using(alias).filter(username=username).exists():
        username = f"{base_username}{counter}"
        counter += 1

    user = User.objects.using(alias).create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        role=User.Role.FRANCHISE_ADMIN,
    )
    logger.info("Created franchise admin %s for %s", username, franchise.slug)
    return user, password


def provision_franchise(
    name: str,
    slug: str,
    *,
    contact_email: str = "",
    contact_phone: str = "",
    hostname: str = "",
    database_url: str = "",
    seed: bool = True,
    admin_email: str = "",
    admin_name: str = "",
) -> tuple[Franchise, str | None]:
    """Create franchise record, database, run migrations, optional seed and admin user."""
    franchise, created = Franchise.objects.get_or_create(
        slug=slug,
        defaults={
            "name": name,
            "contact_email": contact_email,
            "contact_phone": contact_phone,
            "database_url": database_url,
            "status": Franchise.Status.PROVISIONING,
        },
    )
    if not created:
        franchise.name = name
        franchise.contact_email = contact_email
        if contact_phone:
            franchise.contact_phone = contact_phone
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

    admin_password: str | None = None
    if admin_email:
        _, admin_password = create_franchise_admin_user(
            franchise,
            email=admin_email,
            name=admin_name or admin_email,
        )

    franchise.status = Franchise.Status.ACTIVE
    franchise.save(update_fields=["status", "updated_at"])
    logger.info("Provisioned franchise %s on database %s", franchise.slug, alias)
    return franchise, admin_password
