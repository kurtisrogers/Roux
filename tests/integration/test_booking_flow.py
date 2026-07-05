"""Integration tests across app boundaries."""

from datetime import date, time

import pytest
from django.db import IntegrityError
from django.urls import reverse

from accounts.models import User
from bookings.models import Booking, Session
from tests.factories import ChildFactory, OrganisationFactory, SessionTypeFactory, SiteFactory, UserFactory


@pytest.mark.integration
@pytest.mark.django_db
class TestBookingFlow:
    def test_parent_can_view_sessions_after_login(self, client):
        org = OrganisationFactory(slug="flow-club")
        site = SiteFactory(organisation=org)
        st = SessionTypeFactory(organisation=org)
        Session.objects.create(
            organisation=org,
            site=site,
            session_type=st,
            date=date.today(),
            start_time=time(15, 0),
            end_time=time(17, 0),
        )
        parent = UserFactory(role=User.Role.PARENT, organisation=org)
        client.force_login(parent)
        response = client.get(reverse("public:session_list"))
        assert response.status_code == 200
        assert st.name in response.content.decode()

    def test_staff_cannot_access_finance(self, client):
        org = OrganisationFactory()
        staff = UserFactory(role=User.Role.STAFF, organisation=org)
        client.force_login(staff)
        response = client.get(reverse("dashboard:finance"))
        assert response.status_code == 403

    def test_booking_unique_per_child_session(self, client):
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
        parent = UserFactory(role=User.Role.PARENT, organisation=org)
        child = ChildFactory(parent=parent, organisation=org)
        Booking.objects.create(child=child, session=session, booked_by=parent)
        with pytest.raises(IntegrityError):
            Booking.objects.create(child=child, session=session, booked_by=parent)
