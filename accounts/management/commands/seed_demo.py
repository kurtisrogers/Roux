from datetime import date, time, timedelta

from bookings.models import Child, Session, SessionType
from cms.models import NavigationItem, Page, PageBlock, SiteSettings
from django.core.management.base import BaseCommand
from django.utils import timezone
from operations.models import AuthorisedCollector, ChildcareVoucher, RecurringBooking
from organisations.models import Organisation, Site, TermDate

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
        for day_offset in range(1, 15):
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

        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully."))
        self.stdout.write("Login credentials:")
        self.stdout.write("  Admin:  admin / admin123  (dashboard)")
        self.stdout.write("  Super:  superadmin / super123  (platform)")
        self.stdout.write("  Staff:  staff1 / staff123")
        self.stdout.write("  Parent: parent1 / parent123")
