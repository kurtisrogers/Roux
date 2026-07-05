from datetime import date, time

from accounts.models import User
from bookings.models import Session, SessionType
from django.urls import reverse
from organisations.models import Organisation, Site
from rest_framework import status
from rest_framework.test import APITestCase


class ApiAuthTests(APITestCase):
    def setUp(self):
        self.org = Organisation.objects.create(name="Test", slug="test")
        self.user = User.objects.create_user(
            username="parent",
            password="testpass123",
            role=User.Role.PARENT,
            organisation=self.org,
        )

    def test_token_obtain(self):
        response = self.client.post(
            reverse("token_obtain"),
            {"username": "parent", "password": "testpass123"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_me_endpoint(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("me"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "parent")


class SessionApiTests(APITestCase):
    def setUp(self):
        self.org = Organisation.objects.create(name="Test", slug="test")
        self.site = Site.objects.create(organisation=self.org, name="S", slug="s")
        self.user = User.objects.create_user(
            username="parent",
            password="pass",
            role=User.Role.PARENT,
            organisation=self.org,
        )
        st = SessionType.objects.create(organisation=self.org, name="ASC", price="10.00")
        Session.objects.create(
            organisation=self.org,
            site=self.site,
            session_type=st,
            date=date.today(),
            start_time=time(15, 0),
            end_time=time(17, 0),
        )
        self.client.force_authenticate(user=self.user)

    def test_list_sessions(self):
        response = self.client.get("/api/v1/sessions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_upcoming_sessions(self):
        response = self.client.get("/api/v1/sessions/upcoming/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
