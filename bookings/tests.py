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


@pytest.mark.django_db
class TestSessionCapacity:
    def test_spaces_remaining(self):
        org = OrganisationFactory()
        site = SiteFactory(organisation=org)
        st = SessionTypeFactory(organisation=org, capacity=2)
        session = Session.objects.create(
            organisation=org,
            site=site,
            session_type=st,
            date=date.today(),
            start_time=time(15, 0),
            end_time=time(17, 0),
        )
        assert session.spaces_remaining == 2
        assert not session.is_full

        parent = UserFactory(organisation=org)
        for _ in range(2):
            child = ChildFactory(parent=parent, organisation=org)
            Booking.objects.create(
                child=child,
                session=session,
                booked_by=parent,
                status=Booking.Status.CONFIRMED,
            )

        assert session.booked_count == 2
        assert session.spaces_remaining == 0
        assert session.is_full

    def test_child_age_calculation(self):
        child = ChildFactory(date_of_birth=date(2018, 6, 1))
        assert child.age >= 7
