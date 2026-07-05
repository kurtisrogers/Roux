from datetime import date, time
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from accounts.models import User
from bookings.models import Attendance, Booking, Child, Session, SessionType
from organisations.models import Organisation, Site


class NotificationTests(TestCase):
    def setUp(self):
        self.org = Organisation.objects.create(name="T", slug="t")
        self.site = Site.objects.create(organisation=self.org, name="S", slug="s")
        self.parent = User.objects.create_user(
            username="p", email="parent@test.com", password="pass",
            role=User.Role.PARENT, organisation=self.org,
        )
        self.st = SessionType.objects.create(organisation=self.org, name="ASC", price="10.00")
        self.session = Session.objects.create(
            organisation=self.org, site=self.site, session_type=self.st,
            date=date.today(), start_time=time(15, 0), end_time=time(17, 0),
        )
        self.child = Child.objects.create(
            parent=self.parent, organisation=self.org,
            first_name="A", last_name="B", date_of_birth=date(2018, 1, 1),
            emergency_contact_name="EC", emergency_contact_phone="07000",
        )
        self.booking = Booking.objects.create(
            child=self.child, session=self.session, booked_by=self.parent,
            status=Booking.Status.PENDING,
        )

    @patch("notifications.services.send_mail")
    def test_booking_confirmed_sends_email(self, mock_send):
        self.booking.status = Booking.Status.CONFIRMED
        self.booking.save()
        mock_send.assert_called()

    @patch("notifications.services.send_mail")
    def test_check_in_sends_email(self, mock_send):
        self.booking.status = Booking.Status.CONFIRMED
        self.booking.save()
        mock_send.reset_mock()
        attendance = Attendance.objects.create(booking=self.booking)
        attendance.checked_in_at = timezone.now()
        attendance.save()
        mock_send.assert_called()
