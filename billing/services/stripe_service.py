import logging

import stripe
from django.urls import reverse
from franchises.services import get_franchise_stripe_config

from billing.models import Payment

logger = logging.getLogger(__name__)


def _configure_stripe(franchise=None):
    config = get_franchise_stripe_config(franchise)
    stripe.api_key = config["secret_key"]
    return config


def create_booking_checkout_session(booking, request) -> str:
    """Create a Stripe Checkout session for a booking and return the URL."""
    franchise = getattr(request, "franchise", None)
    _configure_stripe(franchise)

    session_type = booking.session.session_type
    success_url = request.build_absolute_uri(
        reverse("public:booking_success", kwargs={"pk": booking.pk})
    )
    cancel_url = request.build_absolute_uri(
        reverse("public:booking_cancel", kwargs={"pk": booking.pk})
    )

    amount_pence = int(session_type.price * 100)
    connect_account = getattr(franchise, "stripe_connect_account_id", "") if franchise else ""

    create_kwargs = {
        "mode": "payment",
        "payment_method_types": ["card"],
        "line_items": [
            {
                "price_data": {
                    "currency": "gbp",
                    "unit_amount": amount_pence,
                    "product_data": {
                        "name": f"{session_type.name} – {booking.session.date}",
                        "description": (f"{booking.child.full_name} – {booking.session.site.name}"),
                    },
                },
                "quantity": 1,
            }
        ],
        "metadata": {
            "booking_id": str(booking.pk),
            "organisation_id": str(booking.session.organisation_id),
        },
        "success_url": success_url + "?session_id={CHECKOUT_SESSION_ID}",
        "cancel_url": cancel_url,
        "customer_email": booking.booked_by.email if booking.booked_by else None,
    }
    if connect_account:
        create_kwargs["stripe_account"] = connect_account

    checkout_session = stripe.checkout.Session.create(**create_kwargs)

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
    franchise = getattr(request, "franchise", None)
    _configure_stripe(franchise)

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


def verify_webhook(payload, sig_header, franchise=None):
    import stripe

    config = get_franchise_stripe_config(franchise)
    if not config["webhook_secret"]:
        raise ValueError("Webhook secret not configured")
    return stripe.Webhook.construct_event(payload, sig_header, config["webhook_secret"])
