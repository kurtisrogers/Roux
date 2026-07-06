from datetime import date, time

import pytest
from bookings.models import Booking, Session
from tests.factories import (
    ChildFactory,
    OrganisationFactory,
    SessionTypeFactory,
    SiteFactory,
    UserFactory,
)

from billing.models import Payment
from billing.services.stripe_service import handle_checkout_completed


@pytest.mark.django_db
class TestStripeService:
    def test_handle_checkout_completed_updates_booking(self):
        org = OrganisationFactory()
        site = SiteFactory(organisation=org)
        st = SessionTypeFactory(organisation=org)
        session = Session.objects.create(
            organisation=org,
            site=site,
            session_type=st,
            date=date.today(),
            start_time=time(15, 0),
            end_time=time(17, 0),
        )
        parent = UserFactory(organisation=org)
        child = ChildFactory(parent=parent, organisation=org)
        booking = Booking.objects.create(
            child=child,
            session=session,
            booked_by=parent,
            status=Booking.Status.PENDING,
        )
        Payment.objects.create(
            organisation=org,
            booking=booking,
            stripe_checkout_session_id="cs_test_123",
            amount="12.00",
        )
        handle_checkout_completed(
            {
                "id": "cs_test_123",
                "payment_intent": "pi_test",
            }
        )
        payment = Payment.objects.get(stripe_checkout_session_id="cs_test_123")
        booking.refresh_from_db()
        assert payment.status == Payment.Status.SUCCEEDED
        assert booking.status == Booking.Status.CONFIRMED
        assert booking.payment_status == Booking.PaymentStatus.PAID
