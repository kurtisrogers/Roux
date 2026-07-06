from datetime import date, time, timedelta
from decimal import Decimal

import pytest
from accounts.models import User
from billing.models import Payment
from bookings.models import Booking, Session
from django.utils import timezone
from tests.factories import (
    ChildFactory,
    OrganisationFactory,
    SessionTypeFactory,
    SiteFactory,
    UserFactory,
)

from operations.models import ChildcareVoucher, RecurringBooking, WaitlistEntry
from operations.services import (
    add_to_waitlist,
    apply_recurring_bookings,
    bulk_check_in,
    calculate_discounted_price,
    get_register_rows,
    redeem_voucher,
)


@pytest.mark.django_db
class TestRegister:
    def test_get_register_rows(self):
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
        Booking.objects.create(
            child=child,
            session=session,
            booked_by=parent,
            status=Booking.Status.CONFIRMED,
        )
        rows = get_register_rows(session)
        assert len(rows) == 1
        assert rows[0]["child"] == child

    def test_bulk_check_in(self):
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
        staff = UserFactory(organisation=org, role=User.Role.STAFF)
        parent = UserFactory(organisation=org)
        child = ChildFactory(parent=parent, organisation=org)
        Booking.objects.create(
            child=child,
            session=session,
            booked_by=parent,
            status=Booking.Status.CONFIRMED,
        )
        count = bulk_check_in(session, staff)
        assert count == 1
        booking = session.bookings.first()
        assert booking.status == Booking.Status.CHECKED_IN


@pytest.mark.django_db
class TestWaitlist:
    def test_promote_waitlist_on_cancellation(self):
        org = OrganisationFactory()
        site = SiteFactory(organisation=org)
        st = SessionTypeFactory(organisation=org, capacity=1)
        session = Session.objects.create(
            organisation=org,
            site=site,
            session_type=st,
            date=date.today(),
            start_time=time(15, 0),
            end_time=time(17, 0),
        )
        parent1 = UserFactory(organisation=org)
        parent2 = UserFactory(organisation=org)
        child1 = ChildFactory(parent=parent1, organisation=org, first_name="A")
        child2 = ChildFactory(parent=parent2, organisation=org, first_name="B")
        booking1 = Booking.objects.create(
            child=child1,
            session=session,
            booked_by=parent1,
            status=Booking.Status.CONFIRMED,
        )
        add_to_waitlist(child2, session)
        assert session.is_full

        booking1.status = Booking.Status.CANCELLED
        booking1.save(update_fields=["status"])

        promoted = Booking.objects.filter(
            child=child2, session=session, source=Booking.Source.WAITLIST
        ).first()
        assert promoted is not None
        assert not WaitlistEntry.objects.filter(session=session).exists()


@pytest.mark.django_db
class TestVouchers:
    def test_redeem_voucher_creates_payment(self):
        org = OrganisationFactory()
        site = SiteFactory(organisation=org)
        st = SessionTypeFactory(organisation=org, price=Decimal("10.00"))
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
            status=Booking.Status.CONFIRMED,
            payment_status=Booking.PaymentStatus.UNPAID,
        )
        voucher = ChildcareVoucher.objects.create(
            organisation=org,
            parent=parent,
            child=child,
            provider="Edenred",
            reference="EDN-001",
            balance=Decimal("50.00"),
        )
        redemption = redeem_voucher(booking, voucher)
        assert redemption.amount == Decimal("10.00")
        voucher.refresh_from_db()
        assert voucher.balance == Decimal("40.00")
        booking.refresh_from_db()
        assert booking.payment_status == Booking.PaymentStatus.PAID
        payment = Payment.objects.get(booking=booking)
        assert payment.payment_method == Payment.Method.VOUCHER


@pytest.mark.django_db
class TestRecurring:
    def test_apply_recurring_bookings(self):
        org = OrganisationFactory()
        site = SiteFactory(organisation=org)
        st = SessionTypeFactory(organisation=org)
        target = timezone.now().date() + timedelta(days=1)
        while target.weekday() >= 5:
            target += timedelta(days=1)
        Session.objects.create(
            organisation=org,
            site=site,
            session_type=st,
            date=target,
            start_time=time(15, 0),
            end_time=time(17, 0),
        )
        parent = UserFactory(organisation=org)
        child = ChildFactory(parent=parent, organisation=org)
        RecurringBooking.objects.create(
            child=child,
            session_type=st,
            site=site,
            weekday=target.weekday(),
            start_date=target - timedelta(days=7),
        )
        created = apply_recurring_bookings(for_date=target)
        assert created == 1
        assert Booking.objects.filter(child=child, source=Booking.Source.RECURRING).exists()


@pytest.mark.django_db
class TestDiscounts:
    def test_pupil_premium_discount(self):
        org = OrganisationFactory()
        st = SessionTypeFactory(organisation=org, price=Decimal("10.00"))
        parent = UserFactory(organisation=org)
        child = ChildFactory(parent=parent, organisation=org, pupil_premium=True)
        price = calculate_discounted_price(st, child, organisation=org)
        assert price == Decimal("8.50")
