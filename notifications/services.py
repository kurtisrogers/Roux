import logging

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def _send(recipient: str, subject: str, template: str, context: dict) -> bool:
    if not recipient:
        return False
    try:
        body = render_to_string(template, context)
        html_body = render_to_string(template.replace(".txt", ".html"), context)
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
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
