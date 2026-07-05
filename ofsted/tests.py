from datetime import date, time

from django.test import TestCase
from django.utils import timezone

from accounts.models import User
from bookings.models import Booking, Child, Session, SessionType
from ofsted.models import Incident, RatioCheck
from ofsted.ratios import analyse_session_ratio, required_staff_count
from ofsted.services import check_session_ratio, generate_monthly_report
from organisations.models import Organisation, Site


class RatioTests(TestCase):
    def test_required_staff_under_fives(self):
        # 8 children aged 4 -> 1:8 ratio -> need 1 staff
        self.assertEqual(required_staff_count([4, 4, 4, 4, 4, 4, 4, 4]), 1)
        # 9 children aged 4 -> need 2 staff
        self.assertEqual(required_staff_count([4] * 9), 2)

    def test_required_staff_mixed_ages(self):
        ages = [4, 4, 4, 4, 4, 4, 4, 4, 4]  # 9 under-5s -> need 2 staff
        result = analyse_session_ratio(ages, staff_count=1)
        self.assertEqual(result["child_count"], 9)
        self.assertFalse(result["compliant"])

    def test_compliant_ratio(self):
        ages = [8, 9]
        result = analyse_session_ratio(ages, staff_count=1)
        self.assertTrue(result["compliant"])


class OfstedServiceTests(TestCase):
    def setUp(self):
        self.org = Organisation.objects.create(name="Test", slug="test")
        self.site = Site.objects.create(organisation=self.org, name="Site", slug="site")
        self.parent = User.objects.create_user(
            username="p", password="pass", role=User.Role.PARENT, organisation=self.org
        )
        self.staff = User.objects.create_user(
            username="s", password="pass", role=User.Role.STAFF, organisation=self.org
        )
        self.st = SessionType.objects.create(
            organisation=self.org, name="ASC", price="10.00"
        )
        self.session = Session.objects.create(
            organisation=self.org,
            site=self.site,
            session_type=self.st,
            date=date.today(),
            start_time=time(15, 0),
            end_time=time(17, 0),
        )
        self.session.staff.add(self.staff)
        self.child = Child.objects.create(
            parent=self.parent,
            organisation=self.org,
            first_name="A",
            last_name="B",
            date_of_birth=date(2018, 1, 1),
            emergency_contact_name="EC",
            emergency_contact_phone="07000000000",
        )
        Booking.objects.create(
            child=self.child,
            session=self.session,
            booked_by=self.parent,
            status=Booking.Status.CONFIRMED,
        )

    def test_ratio_check_creates_record(self):
        check = check_session_ratio(self.session)
        self.assertIsInstance(check, RatioCheck)
        self.assertEqual(check.child_count, 1)

    def test_monthly_report(self):
        report = generate_monthly_report(
            self.org,
            date.today().replace(day=1),
            date.today(),
        )
        self.assertEqual(report.report_type, "monthly")
        self.assertIn("total_sessions", report.data)


class IncidentModelTests(TestCase):
    def test_incident_str(self):
        org = Organisation.objects.create(name="T", slug="t")
        inc = Incident(
            organisation=org,
            incident_type=Incident.Type.ACCIDENT,
            occurred_at=timezone.now(),
            description="Test",
        )
        self.assertIn("Accident", str(inc))
