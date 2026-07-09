from datetime import date, time, timedelta

from billing.models import Payment
from bookings.models import Attendance, Booking, Child, Session, SessionType
from cms.models import NavigationItem, Page, PageBlock, SiteSettings
from django.core.management.base import BaseCommand
from django.utils import timezone
from ofsted.models import Incident
from operations.models import AuthorisedCollector, ChildcareVoucher, RecurringBooking, WaitlistEntry
from organisations.models import Organisation, Site, TermDate
from programme.models import Activity, Programme, WeekPack, WeekPackBlock

from accounts.models import User


class Command(BaseCommand):
    help = "Seed demo organisation with sample wraparound care data"

    def handle(self, *args, **options):
        org, created = Organisation.objects.get_or_create(
            slug="demo-club",
            defaults={
                "name": "Oakwood Wraparound Club",
                "email": "hello@oakwood-club.example",
                "phone": "01234 567890",
                "address_line1": "Oakwood Primary School",
                "city": "Manchester",
                "county": "Greater Manchester",
                "postcode": "M1 1AA",
                "ofsted_number": "EY123456",
            },
        )
        self.stdout.write(f"Organisation: {org.name} ({'created' if created else 'exists'})")

        site, _ = Site.objects.get_or_create(
            organisation=org,
            slug="oakwood-primary",
            defaults={
                "name": "Oakwood Primary",
                "city": "Manchester",
                "postcode": "M1 1AA",
                "capacity": 40,
            },
        )

        TermDate.objects.get_or_create(
            organisation=org,
            name="Summer Term 2026",
            defaults={
                "start_date": date(2026, 4, 14),
                "end_date": date(2026, 7, 17),
            },
        )

        breakfast, _ = SessionType.objects.get_or_create(
            organisation=org,
            name="Breakfast Club",
            defaults={
                "category": SessionType.Category.BREAKFAST,
                "description": "Early morning care with breakfast from 7:30am.",
                "price": "6.50",
                "capacity": 25,
                "age_min": 4,
                "age_max": 11,
                "duration_minutes": 60,
            },
        )
        after_school, _ = SessionType.objects.get_or_create(
            organisation=org,
            name="After School Club",
            defaults={
                "category": SessionType.Category.AFTER_SCHOOL,
                "description": "Activities, homework help and snacks until 6pm.",
                "price": "12.00",
                "capacity": 35,
                "age_min": 4,
                "age_max": 11,
                "duration_minutes": 120,
            },
        )

        admin_user, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@oakwood-club.example",
                "first_name": "Alex",
                "last_name": "Manager",
                "role": User.Role.ORG_ADMIN,
                "organisation": org,
                "is_staff": True,
            },
        )
        if created:
            admin_user.set_password("admin123")
            admin_user.save()

        super_admin, created = User.objects.get_or_create(
            username="superadmin",
            defaults={
                "email": "platform@roux.example",
                "first_name": "Platform",
                "last_name": "Admin",
                "role": User.Role.SUPER_ADMIN,
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            super_admin.set_password("super123")
            super_admin.save()

        staff_user, created = User.objects.get_or_create(
            username="staff1",
            defaults={
                "email": "staff@oakwood-club.example",
                "first_name": "Jamie",
                "last_name": "Taylor",
                "role": User.Role.STAFF,
                "organisation": org,
                "site": site,
            },
        )
        if created:
            staff_user.set_password("staff123")
            staff_user.save()

        parent, created = User.objects.get_or_create(
            username="parent1",
            defaults={
                "email": "parent@example.com",
                "first_name": "Sarah",
                "last_name": "Johnson",
                "role": User.Role.PARENT,
                "organisation": org,
            },
        )
        if created:
            parent.set_password("parent123")
            parent.save()

        SiteSettings.objects.get_or_create(
            organisation=org,
            defaults={
                "site_name": "Oakwood Wraparound Club",
                "tagline": "Safe, fun care before and after school",
                "primary_colour": "#1a5fb4",
                "contact_email": "hello@oakwood-club.example",
                "contact_phone": "01234 567890",
                "footer_text": "© Oakwood Wraparound Club. Registered with Ofsted.",
            },
        )

        page, created = Page.objects.get_or_create(
            organisation=org,
            slug="home",
            defaults={
                "title": "Home",
                "is_homepage": True,
                "is_published": True,
                "meta_description": "Oakwood Wraparound Club – breakfast and after school care in Manchester.",
            },
        )

        if created or not page.blocks.exists():
            PageBlock.objects.filter(page=page).delete()
            blocks = [
                (
                    PageBlock.BlockType.HERO,
                    {
                        "title": "Oakwood Wraparound Club",
                        "subtitle": "Ofsted-registered breakfast and after school care in Manchester",
                        "cta_text": "Book a Session",
                        "cta_url": "/sessions/",
                    },
                ),
                (
                    PageBlock.BlockType.FEATURES,
                    {
                        "items": [
                            {
                                "title": "Qualified Staff",
                                "description": "DBS-checked, first-aid trained team.",
                            },
                            {
                                "title": "Flexible Booking",
                                "description": "Book individual sessions online.",
                            },
                            {
                                "title": "Healthy Food",
                                "description": "Nutritious breakfast and snacks included.",
                            },
                        ],
                    },
                ),
                (PageBlock.BlockType.SESSION_LIST, {}),
                (PageBlock.BlockType.PRICING, {}),
                (
                    PageBlock.BlockType.FAQ,
                    {
                        "items": [
                            {
                                "question": "What time does breakfast club start?",
                                "answer": "Breakfast club runs from 7:30am until school starts.",
                            },
                            {
                                "question": "Can I book ad-hoc sessions?",
                                "answer": "Yes, subject to availability. Book online anytime.",
                            },
                        ],
                    },
                ),
                (
                    PageBlock.BlockType.CTA,
                    {
                        "title": "Join us today",
                        "text": "Register your child and book your first session.",
                        "button_text": "Register Now",
                        "button_url": "/accounts/register/",
                    },
                ),
            ]
            for order, (block_type, content) in enumerate(blocks):
                PageBlock.objects.create(
                    page=page,
                    block_type=block_type,
                    order=order,
                    content=content,
                )

        about_page, _ = Page.objects.get_or_create(
            organisation=org,
            slug="about",
            defaults={
                "title": "About Us",
                "is_published": True,
                "meta_description": "Learn about Oakwood Wraparound Club.",
            },
        )
        if not about_page.blocks.exists():
            PageBlock.objects.create(
                page=about_page,
                block_type=PageBlock.BlockType.RICH_TEXT,
                order=0,
                content={
                    "body": (
                        "<p>We have been providing wraparound care at Oakwood Primary "
                        "for over 10 years. Our experienced team creates a safe, "
                        "welcoming environment where children can play, learn and relax.</p>"
                    ),
                },
            )

        NavigationItem.objects.get_or_create(
            organisation=org,
            label="Home",
            defaults={"page": page, "order": 0},
        )
        NavigationItem.objects.get_or_create(
            organisation=org,
            label="About",
            defaults={"page": about_page, "order": 1},
        )

        today = timezone.now().date()
        for day_offset in range(0, 15):
            session_date = today + timedelta(days=day_offset)
            if session_date.weekday() >= 5:
                continue
            Session.objects.get_or_create(
                organisation=org,
                site=site,
                session_type=after_school,
                date=session_date,
                start_time=time(15, 15),
                defaults={"end_time": time(17, 15)},
            )
            Session.objects.get_or_create(
                organisation=org,
                site=site,
                session_type=breakfast,
                date=session_date,
                start_time=time(7, 30),
                defaults={"end_time": time(8, 30)},
            )

        child, _ = Child.objects.get_or_create(
            parent=parent,
            organisation=org,
            first_name="Emily",
            last_name="Johnson",
            defaults={
                "date_of_birth": date(2017, 3, 15),
                "emergency_contact_name": "Sarah Johnson",
                "emergency_contact_phone": "07700900123",
            },
        )

        AuthorisedCollector.objects.get_or_create(
            child=child,
            name="Grandma Pat",
            defaults={
                "relationship": "Grandmother",
                "phone": "07700900456",
                "pin_code": "1234",
                "is_primary": True,
            },
        )

        RecurringBooking.objects.get_or_create(
            child=child,
            session_type=after_school,
            site=site,
            weekday=RecurringBooking.Weekday.TUESDAY,
            defaults={"start_date": today},
        )

        ChildcareVoucher.objects.get_or_create(
            organisation=org,
            parent=parent,
            reference="EDEN-1001",
            defaults={
                "child": child,
                "provider": "Edenred",
                "balance": "120.00",
            },
        )

        snack, _ = Activity.objects.get_or_create(
            organisation=org,
            name="Snack time",
            defaults={"category": Activity.Category.FOOD, "default_duration_minutes": 15},
        )
        football, _ = Activity.objects.get_or_create(
            organisation=org,
            name="Football",
            defaults={"category": Activity.Category.SPORT, "default_duration_minutes": 45},
        )
        crafts, _ = Activity.objects.get_or_create(
            organisation=org,
            name="Arts & crafts",
            defaults={"category": Activity.Category.CREATIVE, "default_duration_minutes": 45},
        )
        homework, _ = Activity.objects.get_or_create(
            organisation=org,
            name="Homework club",
            defaults={"category": Activity.Category.QUIET, "default_duration_minutes": 30},
        )

        week_a, _ = WeekPack.objects.get_or_create(
            organisation=org,
            name="Week A",
            defaults={"description": "Standard after-school rotation"},
        )
        week_b, _ = WeekPack.objects.get_or_create(
            organisation=org,
            name="Week B",
            defaults={"description": "Alternate after-school rotation"},
        )

        def _ensure_block(pack, weekday, start_h, start_m, end_h, end_m, activity, order):
            WeekPackBlock.objects.get_or_create(
                week_pack=pack,
                weekday=weekday,
                start_time=time(start_h, start_m),
                defaults={
                    "end_time": time(end_h, end_m),
                    "activity": activity,
                    "sort_order": order,
                },
            )

        for weekday in range(0, 5):
            _ensure_block(week_a, weekday, 15, 15, 15, 30, snack, 0)
            _ensure_block(
                week_a, weekday, 15, 30, 16, 15, football if weekday % 2 == 0 else crafts, 1
            )
            _ensure_block(week_a, weekday, 16, 15, 17, 0, homework, 2)
            _ensure_block(week_b, weekday, 15, 15, 15, 30, snack, 0)
            _ensure_block(
                week_b, weekday, 15, 30, 16, 15, crafts if weekday % 2 == 0 else football, 1
            )
            _ensure_block(week_b, weekday, 16, 15, 17, 0, homework, 2)

        term_end = today + timedelta(days=90)
        programme, _ = Programme.objects.get_or_create(
            organisation=org,
            site=site,
            session_type=after_school,
            name="Summer term after-school",
            defaults={
                "start_date": today,
                "end_date": term_end,
                "week_a_pack": week_a,
                "week_b_pack": week_b,
                "anchor_date": today,
                "first_week": Programme.FirstWeek.A,
                "status": Programme.Status.PUBLISHED,
            },
        )

        self._seed_families_and_bookings(
            org=org,
            site=site,
            staff_user=staff_user,
            parent=parent,
            child=child,
            breakfast=breakfast,
            after_school=after_school,
            today=today,
        )

        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully."))
        self.stdout.write("Login credentials:")
        self.stdout.write("  Admin:  admin / admin123  (dashboard)")
        self.stdout.write("  Super:  superadmin / super123  (platform)")
        self.stdout.write("  Staff:  staff1 / staff123")
        self.stdout.write("  Parent: parent1 / parent123")

    def _seed_families_and_bookings(
        self, *, org, site, staff_user, parent, child, breakfast, after_school, today
    ):
        """Populate realistic bookings, attendance, payments, and waitlist data."""
        families = [
            (
                parent,
                child,
                [
                    {
                        "first_name": "Emily",
                        "last_name": "Johnson",
                        "date_of_birth": date(2017, 3, 15),
                        "allergies": "Peanuts",
                        "medical_notes": "EpiPen in school office",
                        "school_year": "Year 4",
                    },
                ],
            ),
            (
                self._ensure_parent(
                    org,
                    "parent2",
                    "marcus.williams@example.com",
                    "Marcus",
                    "Williams",
                ),
                None,
                [
                    {
                        "first_name": "Noah",
                        "last_name": "Williams",
                        "date_of_birth": date(2016, 8, 2),
                        "pupil_premium": True,
                        "school_year": "Year 5",
                    },
                    {
                        "first_name": "Olivia",
                        "last_name": "Williams",
                        "date_of_birth": date(2019, 1, 20),
                        "school_year": "Year 2",
                    },
                ],
            ),
            (
                self._ensure_parent(
                    org,
                    "parent3",
                    "priya.davis@example.com",
                    "Priya",
                    "Davis",
                ),
                None,
                [
                    {
                        "first_name": "Liam",
                        "last_name": "Davis",
                        "date_of_birth": date(2018, 5, 11),
                        "allergies": "Dairy",
                        "dietary_requirements": "Dairy-free snacks only",
                        "fsm_eligible": True,
                        "school_year": "Year 3",
                    },
                ],
            ),
            (
                self._ensure_parent(
                    org,
                    "parent4",
                    "emma.taylor@example.com",
                    "Emma",
                    "Taylor",
                ),
                None,
                [
                    {
                        "first_name": "Mason",
                        "last_name": "Taylor",
                        "date_of_birth": date(2017, 11, 4),
                        "school_year": "Year 4",
                    },
                    {
                        "first_name": "Grace",
                        "last_name": "Taylor",
                        "date_of_birth": date(2015, 6, 30),
                        "school_year": "Year 6",
                    },
                ],
            ),
            (
                self._ensure_parent(
                    org,
                    "parent5",
                    "james.anderson@example.com",
                    "James",
                    "Anderson",
                ),
                None,
                [
                    {
                        "first_name": "Isla",
                        "last_name": "Anderson",
                        "date_of_birth": date(2018, 9, 14),
                        "medical_notes": "Mild asthma – inhaler with child",
                        "school_year": "Year 3",
                    },
                    {
                        "first_name": "Harry",
                        "last_name": "Anderson",
                        "date_of_birth": date(2016, 2, 8),
                        "school_year": "Year 5",
                    },
                ],
            ),
            (
                self._ensure_parent(
                    org,
                    "parent6",
                    "sofia.martinez@example.com",
                    "Sofia",
                    "Martinez",
                ),
                None,
                [
                    {
                        "first_name": "Sophia",
                        "last_name": "Martinez",
                        "date_of_birth": date(2017, 7, 22),
                        "pupil_premium": True,
                        "school_year": "Year 4",
                    },
                    {
                        "first_name": "Jack",
                        "last_name": "Martinez",
                        "date_of_birth": date(2019, 4, 3),
                        "allergies": "Eggs",
                        "school_year": "Year 1",
                    },
                ],
            ),
        ]

        children = []
        for family_parent, existing_child, child_specs in families:
            for index, spec in enumerate(child_specs):
                if existing_child and index == 0:
                    child_obj = existing_child
                    Child.objects.filter(pk=child_obj.pk).update(
                        allergies=spec.get("allergies", ""),
                        medical_notes=spec.get("medical_notes", ""),
                        dietary_requirements=spec.get("dietary_requirements", ""),
                        school_year=spec.get("school_year", ""),
                        pupil_premium=spec.get("pupil_premium", False),
                        fsm_eligible=spec.get("fsm_eligible", False),
                    )
                    child_obj.refresh_from_db()
                else:
                    child_obj, _ = Child.objects.get_or_create(
                        parent=family_parent,
                        organisation=org,
                        first_name=spec["first_name"],
                        last_name=spec["last_name"],
                        defaults={
                            "date_of_birth": spec["date_of_birth"],
                            "emergency_contact_name": family_parent.get_full_name(),
                            "emergency_contact_phone": "07700900123",
                            "emergency_contact_relationship": "Parent",
                            "allergies": spec.get("allergies", ""),
                            "medical_notes": spec.get("medical_notes", ""),
                            "dietary_requirements": spec.get("dietary_requirements", ""),
                            "school_year": spec.get("school_year", ""),
                            "pupil_premium": spec.get("pupil_premium", False),
                            "fsm_eligible": spec.get("fsm_eligible", False),
                            "photo_consent": True,
                        },
                    )
                children.append(child_obj)

        breakfast_sessions = list(
            Session.objects.filter(
                organisation=org,
                session_type=breakfast,
                date__gte=today,
                date__lte=today + timedelta(days=10),
            ).order_by("date", "start_time")
        )
        after_school_sessions = list(
            Session.objects.filter(
                organisation=org,
                session_type=after_school,
                date__gte=today,
                date__lte=today + timedelta(days=10),
            ).order_by("date", "start_time")
        )

        if not breakfast_sessions:
            return

        register_session = breakfast_sessions[0]
        now = timezone.now()

        for index, child_obj in enumerate(children):
            target_sessions = []
            if index % 2 == 0 and breakfast_sessions:
                target_sessions.append(breakfast_sessions[index % len(breakfast_sessions)])
            if after_school_sessions:
                target_sessions.append(after_school_sessions[index % len(after_school_sessions)])
            if len(target_sessions) < 2 and len(breakfast_sessions) > 1:
                target_sessions.append(breakfast_sessions[1])

            for session in target_sessions[:3]:
                booking, created = Booking.objects.get_or_create(
                    child=child_obj,
                    session=session,
                    defaults={
                        "booked_by": child_obj.parent,
                        "status": Booking.Status.CONFIRMED,
                        "payment_status": Booking.PaymentStatus.PAID
                        if index % 3 != 0
                        else Booking.PaymentStatus.UNPAID,
                        "source": Booking.Source.ONLINE,
                    },
                )
                if created and booking.payment_status == Booking.PaymentStatus.PAID:
                    Payment.objects.get_or_create(
                        organisation=org,
                        booking=booking,
                        defaults={
                            "amount": session.session_type.price,
                            "status": Payment.Status.SUCCEEDED,
                            "payment_method": Payment.Method.CARD,
                            "description": f"{session.session_type.name} – {child_obj.full_name}",
                        },
                    )

        for index, child_obj in enumerate(children[:9]):
            booking = Booking.objects.filter(child=child_obj, session=register_session).first()
            if not booking:
                booking = Booking.objects.create(
                    child=child_obj,
                    session=register_session,
                    booked_by=child_obj.parent,
                    status=Booking.Status.CONFIRMED,
                    payment_status=Booking.PaymentStatus.PAID,
                    source=Booking.Source.ONLINE,
                )
                Payment.objects.get_or_create(
                    organisation=org,
                    booking=booking,
                    defaults={
                        "amount": register_session.session_type.price,
                        "status": Payment.Status.SUCCEEDED,
                        "payment_method": Payment.Method.CARD,
                        "description": f"Breakfast Club – {child_obj.full_name}",
                    },
                )

            attendance, _ = Attendance.objects.get_or_create(booking=booking)
            check_in_time = now.replace(hour=7, minute=35 + index, second=0, microsecond=0)
            Attendance.objects.filter(pk=attendance.pk).update(
                checked_in_at=check_in_time,
                checked_in_by=staff_user,
            )
            if index < 3:
                Attendance.objects.filter(pk=attendance.pk).update(
                    checked_out_at=check_in_time + timedelta(minutes=45),
                    checked_out_by=staff_user,
                    collection_verified_name="Parent collection",
                )
                Booking.objects.filter(pk=booking.pk).update(status=Booking.Status.CHECKED_OUT)
            else:
                Booking.objects.filter(pk=booking.pk).update(status=Booking.Status.CHECKED_IN)

        full_session = after_school_sessions[0] if after_school_sessions else None
        if full_session:
            for child_obj in children:
                booking, _ = Booking.objects.get_or_create(
                    child=child_obj,
                    session=full_session,
                    defaults={
                        "booked_by": child_obj.parent,
                        "status": Booking.Status.CONFIRMED,
                        "payment_status": Booking.PaymentStatus.PAID,
                        "source": Booking.Source.ONLINE,
                    },
                )
                if booking.payment_status == Booking.PaymentStatus.PAID:
                    Payment.objects.get_or_create(
                        organisation=org,
                        booking=booking,
                        defaults={
                            "amount": full_session.session_type.price,
                            "status": Payment.Status.SUCCEEDED,
                            "payment_method": Payment.Method.CARD,
                            "description": f"After School Club – {child_obj.full_name}",
                        },
                    )

            overflow_children = children[-2:]
            for position, child_obj in enumerate(overflow_children, start=1):
                WaitlistEntry.objects.get_or_create(
                    child=child_obj,
                    session=full_session,
                    defaults={"position": position},
                )

        Incident.objects.get_or_create(
            organisation=org,
            child=children[0],
            incident_type=Incident.Type.ACCIDENT,
            occurred_at=now - timedelta(days=2),
            defaults={
                "session": register_session,
                "severity": Incident.Severity.LOW,
                "location": "Playground",
                "description": "Minor scrape on knee during outdoor play. Cleaned and plaster applied.",
                "action_taken": "First aid administered; parent informed at collection.",
                "parent_notified": True,
                "parent_notified_at": now - timedelta(days=2, hours=2),
                "reported_by": staff_user,
            },
        )

    def _ensure_parent(self, org, username, email, first_name, last_name):
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "role": User.Role.PARENT,
                "organisation": org,
            },
        )
        if created:
            user.set_password("parent123")
            user.save()
        return user
