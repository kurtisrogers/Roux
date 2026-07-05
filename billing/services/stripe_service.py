import logging
from decimal import Decimal

import stripe
from django.conf import settings
from django.urls import reverse

from billing.models import Payment

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_booking_checkout_session(booking, request) -> str:
    """Create a Stripe Checkout session for a booking and return the URL."""
    session_type = booking.session.session_type
    success_url = request.build_absolute_uri(
        reverse("public:booking_success", kwargs={"pk": booking.pk})
    )
    cancel_url = request.build_absolute_uri(
        reverse("public:booking_cancel", kwargs={"pk": booking.pk})
    )

    amount_pence = int(session_type.price * 100)

    checkout_session = stripe.checkout.Session.create(
        mode="payment",
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "gbp",
                    "unit_amount": amount_pence,
                    "product_data": {
                        "name": f"{session_type.name} – {booking.session.date}",
                        "description": (
                            f"{booking.child.full_name} – "
                            f"{booking.session.site.name}"
                        ),
                    },
                },
                "quantity": 1,
            }
        ],
        metadata={
            "booking_id": str(booking.pk),
            "organisation_id": str(booking.session.organisation_id),
        },
        success_url=success_url + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=cancel_url,
        customer_email=booking.booked_by.email if booking.booked_by else None,
    )

    Payment.objects.create(
        organisation=booking.session.organisation,
        booking=booking,
        stripe_checkout_session_id=checkout_session.id,
        amount=session_type.price,
        status=Payment.Status.PENDING,
        description=f"Booking: {booking.child.full_name} – {session_type.name}",
        metadata={"booking_id": booking.pk},
    )

    booking.payment_status = booking.PaymentStatus.PENDING
    booking.save(update_fields=["payment_status"])

    return checkout_session.url


def handle_checkout_completed(session_data: dict) -> None:
    session_id = session_data.get("id")
    payment = Payment.objects.filter(stripe_checkout_session_id=session_id).first()
    if not payment:
        logger.warning("No payment found for checkout session %s", session_id)
        return

    payment.status = Payment.Status.SUCCEEDED
    payment.stripe_payment_intent_id = session_data.get("payment_intent", "")
    payment.save()

    if payment.booking:
        booking = payment.booking
        booking.payment_status = booking.PaymentStatus.PAID
        booking.status = booking.Status.CONFIRMED
        booking.save(update_fields=["payment_status", "status"])

        from notifications.services import notify_payment_received

        notify_payment_received(booking, payment)


def create_org_subscription_checkout(organisation, request) -> str:
    """Create Stripe Checkout for organisation SaaS subscription."""
    success_url = request.build_absolute_uri(reverse("dashboard:billing_success"))
    cancel_url = request.build_absolute_uri(reverse("dashboard:billing"))

    checkout_session = stripe.checkout.Session.create(
        mode="subscription",
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "gbp",
                    "unit_amount": 4900,
                    "recurring": {"interval": "month"},
                    "product_data": {
                        "name": "Roux Standard Plan",
                        "description": "Wraparound care management platform",
                    },
                },
                "quantity": 1,
            }
        ],
        metadata={"organisation_id": str(organisation.pk)},
        success_url=success_url + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=cancel_url,
        customer_email=organisation.email or None,
    )
    return checkout_session.url
