from django.test import Client, TestCase

from accounts.models import User
from cms.models import Page
from organisations.models import Organisation


class PublicSiteTests(TestCase):
    def setUp(self):
        self.org = Organisation.objects.create(name="Test Club", slug="test-club")
        Page.objects.create(
            organisation=self.org,
            title="Home",
            slug="home",
            is_homepage=True,
            is_published=True,
        )
        self.client = Client()

    def test_homepage_loads(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_sessions_page(self):
        response = self.client.get("/sessions/")
        self.assertEqual(response.status_code, 200)


class DashboardAccessTests(TestCase):
    def setUp(self):
        self.org = Organisation.objects.create(name="Test Club", slug="test-club")
        self.admin = User.objects.create_user(
            username="admin",
            password="pass",
            role=User.Role.ORG_ADMIN,
            organisation=self.org,
        )
        self.parent = User.objects.create_user(
            username="parent",
            password="pass",
            role=User.Role.PARENT,
            organisation=self.org,
        )
        self.client = Client()

    def test_admin_can_access_dashboard(self):
        self.client.login(username="admin", password="pass")
        response = self.client.get("/dashboard/")
        self.assertEqual(response.status_code, 200)

    def test_parent_cannot_access_dashboard(self):
        self.client.login(username="parent", password="pass")
        response = self.client.get("/dashboard/")
        self.assertEqual(response.status_code, 403)


class UserModelTests(TestCase):
    def test_role_properties(self):
        admin = User(role=User.Role.ORG_ADMIN)
        self.assertTrue(admin.is_dashboard_user)
        parent = User(role=User.Role.PARENT)
        self.assertFalse(parent.is_dashboard_user)
