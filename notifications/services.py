import logging

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def _from_email(franchise=None) -> str:
    if franchise and getattr(franchise, "default_from_email", ""):
        return franchise.default_from_email
    return settings.DEFAULT_FROM_EMAIL


def _send(
    recipient: str,
    subject: str,
    template: str,
    context: dict,
    *,
    from_email: str | None = None,
) -> bool:
    if not recipient:
        return False
    try:
        body = render_to_string(template, context)
        html_body = render_to_string(template.replace(".txt", ".html"), context)
        send_mail(
            subject=subject,
            message=body,
            from_email=from_email or settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            html_message=html_body,
            fail_silently=False,
        )
        return True
    except Exception:
        logger.exception("Failed to send email to %s: %s", recipient, subject)
        return False


def notify_booking_confirmed(booking) -> bool:
    parent = booking.booked_by or booking.child.parent
    return _send(
        parent.email,
        f"Booking confirmed – {booking.session.session_type.name}",
        "emails/booking_confirmed.txt",
        {"booking": booking, "parent": parent},
    )


def notify_payment_received(booking, payment) -> bool:
    parent = booking.booked_by or booking.child.parent
    return _send(
        parent.email,
        f"Payment received – £{payment.amount}",
        "emails/payment_received.txt",
        {"booking": booking, "payment": payment, "parent": parent},
    )


def notify_checked_in(booking) -> bool:
    parent = booking.child.parent
    return _send(
        parent.email,
        f"{booking.child.first_name} checked in",
        "emails/checked_in.txt",
        {"booking": booking, "parent": parent},
    )


def notify_checked_out(booking) -> bool:
    parent = booking.child.parent
    return _send(
        parent.email,
        f"{booking.child.first_name} checked out",
        "emails/checked_out.txt",
        {"booking": booking, "parent": parent},
    )


def notify_staff_session_reminder(session) -> int:
    sent = 0
    for staff_member in session.staff.filter(email__gt=""):
        if _send(
            staff_member.email,
            f"Session tomorrow: {session.session_type.name}",
            "emails/session_reminder.txt",
            {"session": session, "staff": staff_member},
        ):
            sent += 1
    return sent


def notify_franchise_application_received(application) -> bool:
    return _send(
        application.email,
        "We've received your Roux franchise application",
        "emails/franchise_application_received.txt",
        {"application": application},
    )


def notify_franchise_application_under_review(application) -> bool:
    return _send(
        application.email,
        "Your Roux franchise application is under review",
        "emails/franchise_application_under_review.txt",
        {"application": application},
    )


def notify_franchise_application_partner(application, franchise, temp_password: str) -> bool:
    return _send(
        application.email,
        f"Welcome to Roux – {franchise.name} is ready",
        "emails/franchise_application_partner.txt",
        {
            "application": application,
            "franchise": franchise,
            "temp_password": temp_password,
        },
    )


def notify_franchise_application_rejected(application) -> bool:
    return _send(
        application.email,
        "Update on your Roux franchise application",
        "emails/franchise_application_rejected.txt",
        {"application": application},
    )


def notify_platform_new_application(application) -> bool:
    platform_email = getattr(settings, "PLATFORM_ADMIN_EMAIL", "")
    if not platform_email:
        return False
    return _send(
        platform_email,
        f"New franchise application: {application.business_name}",
        "emails/franchise_application_platform_alert.txt",
        {"application": application},
    )
