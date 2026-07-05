import logging
import secrets
from datetime import datetime

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from franchises.db import build_franchise_database_url, create_franchise_database
from franchises.models import Franchise, FranchiseApplication
from franchises.services import provision_franchise
from notifications.services import (
    notify_franchise_application_partner,
    notify_franchise_application_received,
    notify_franchise_application_rejected,
    notify_franchise_application_under_review,
    notify_platform_new_application,
)

logger = logging.getLogger(__name__)


def generate_application_reference() -> str:
    return secrets.token_urlsafe(12)


def unique_slug_from_business_name(business_name: str) -> str:
    base = slugify(business_name) or "franchise"
    slug = base
    counter = 1
    while FranchiseApplication.objects.filter(proposed_slug=slug).exists() or Franchise.objects.filter(
        slug=slug
    ).exists():
        slug = f"{base}-{counter}"
        counter += 1
    return slug


def submit_franchise_application(
    *,
    applicant_name: str,
    business_name: str,
    email: str,
    phone: str = "",
    region: str = "",
    experience_years: int | None = None,
    message: str = "",
    proposed_slug: str = "",
) -> FranchiseApplication:
    slug = proposed_slug or unique_slug_from_business_name(business_name)
    application = FranchiseApplication.objects.create(
        reference=generate_application_reference(),
        applicant_name=applicant_name,
        business_name=business_name,
        proposed_slug=slug,
        email=email,
        phone=phone,
        region=region,
        experience_years=experience_years,
        message=message,
        status=FranchiseApplication.Status.PENDING,
    )
    notify_franchise_application_received(application)
    notify_platform_new_application(application)
    return application


def _partner_hostname(slug: str) -> str:
    base_domain = getattr(settings, "FRANCHISE_BASE_DOMAIN", "localhost")
    return f"{slug}.{base_domain}"


def _provision_database_url(slug: str) -> str:
    template = getattr(settings, "FRANCHISE_DATABASE_URL_TEMPLATE", "")
    if not template:
        return ""
    db_name = f"roux_franchise_{slug.replace('-', '_')}"
    create_franchise_database(db_name)
    return build_franchise_database_url(slug, db_name=db_name)


@transaction.atomic
def set_application_status(
    application: FranchiseApplication,
    status: str,
    *,
    admin_notes: str = "",
) -> FranchiseApplication:
    previous = application.status
    application.status = status
    if admin_notes:
        application.admin_notes = admin_notes
    application.reviewed_at = timezone.now()
    application.save()

    if status == FranchiseApplication.Status.UNDER_REVIEW and previous != status:
        notify_franchise_application_under_review(application)
    elif status == FranchiseApplication.Status.REJECTED and previous != status:
        notify_franchise_application_rejected(application)
    elif status == FranchiseApplication.Status.PARTNER and not application.franchise_id:
        application = _approve_as_partner(application)

    return application


def _approve_as_partner(application: FranchiseApplication) -> FranchiseApplication:
    database_url = _provision_database_url(application.proposed_slug)
    franchise, temp_password = provision_franchise(
        name=application.business_name,
        slug=application.proposed_slug,
        contact_email=application.email,
        contact_phone=application.phone,
        hostname=_partner_hostname(application.proposed_slug),
        database_url=database_url,
        seed=False,
        admin_email=application.email,
        admin_name=application.applicant_name,
    )
    application.franchise = franchise
    application.save(update_fields=["franchise", "updated_at"])

    notify_franchise_application_partner(application, franchise, temp_password or "")
    logger.info("Approved franchise application %s as partner %s", application.reference, franchise.slug)
    return application
