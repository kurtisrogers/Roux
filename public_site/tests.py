from datetime import date, time

from accounts.models import User
from bookings.models import Booking, Child, Session, SessionType
from django.test import TestCase
from django.urls import reverse
from organisations.models import Organisation, Site


class BookingTenantIsolationTests(TestCase):
    def setUp(self):
        self.org_a = Organisation.objects.create(name="Org A", slug="org-a")
        self.org_b = Organisation.objects.create(name="Org B", slug="org-b")
        self.site_a = Site.objects.create(organisation=self.org_a, name="Site A", slug="site-a")
        self.site_b = Site.objects.create(organisation=self.org_b, name="Site B", slug="site-b")

        self.parent_a = User.objects.create_user(
            username="parent_a",
            email="a@test.com",
            password="pass",
            role=User.Role.PARENT,
            organisation=self.org_a,
        )
        self.parent_b = User.objects.create_user(
            username="parent_b",
            email="b@test.com",
            password="pass",
            role=User.Role.PARENT,
            organisation=self.org_b,
        )

        st_a = SessionType.objects.create(organisation=self.org_a, name="ASC", price="10.00")
        st_b = SessionType.objects.create(organisation=self.org_b, name="ASC", price="10.00")
        self.session_a = Session.objects.create(
            organisation=self.org_a,
            site=self.site_a,
            session_type=st_a,
            date=date.today(),
            start_time=time(15, 0),
            end_time=time(17, 0),
        )
        self.session_b = Session.objects.create(
            organisation=self.org_b,
            site=self.site_b,
            session_type=st_b,
            date=date.today(),
            start_time=time(15, 0),
            end_time=time(17, 0),
        )

        child_a = Child.objects.create(
            parent=self.parent_a,
            organisation=self.org_a,
            first_name="Child",
            last_name="A",
            date_of_birth=date(2018, 1, 1),
            emergency_contact_name="EC",
            emergency_contact_phone="07000",
        )
        child_b = Child.objects.create(
            parent=self.parent_b,
            organisation=self.org_b,
            first_name="Child",
            last_name="B",
            date_of_birth=date(2018, 1, 1),
            emergency_contact_name="EC",
            emergency_contact_phone="07000",
        )

        self.booking_a = Booking.objects.create(
            child=child_a,
            session=self.session_a,
            booked_by=self.parent_a,
        )
        self.booking_b = Booking.objects.create(
            child=child_b,
            session=self.session_b,
            booked_by=self.parent_b,
        )

    def test_my_bookings_scoped_to_organisation(self):
        self.client.login(username="parent_a", password="pass")
        response = self.client.get(
            f"{reverse('public:my_bookings')}?org=org-a",
            HTTP_HOST="testserver",
        )
        assert response.status_code == 200
        bookings = list(response.context["bookings"])
        assert self.booking_a in bookings
        assert self.booking_b not in bookings

    def test_booking_cancel_requires_owner(self):
        self.client.login(username="parent_b", password="pass")
        response = self.client.get(
            f"{reverse('public:booking_cancel', kwargs={'pk': self.booking_a.pk})}?org=org-a",
            HTTP_HOST="testserver",
        )
        assert response.status_code == 404

    def test_booking_cancel_by_owner_succeeds(self):
        self.client.login(username="parent_a", password="pass")
        response = self.client.get(
            f"{reverse('public:booking_cancel', kwargs={'pk': self.booking_a.pk})}?org=org-a",
            HTTP_HOST="testserver",
        )
        assert response.status_code == 302
        self.booking_a.refresh_from_db()
        assert self.booking_a.status == Booking.Status.CANCELLED
