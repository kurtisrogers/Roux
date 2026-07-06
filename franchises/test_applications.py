from unittest.mock import MagicMock, patch

import pytest
from accounts.models import User
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from franchises.application_services import set_application_status, submit_franchise_application
from franchises.models import Franchise, FranchiseApplication
from franchises.services import create_franchise_admin_user, provision_franchise


@pytest.mark.django_db
class TestFranchiseApplicationFlow:
    @patch("franchises.application_services.notify_platform_new_application")
    def test_submit_application_sends_confirmation_email(self, mock_platform):
        submit_franchise_application(
            applicant_name="Jane Smith",
            business_name="North Star Clubs",
            email="jane@example.com",
            region="Greater Manchester",
        )
        assert len(mail.outbox) == 1
        assert "received" in mail.outbox[0].subject.lower()
        mock_platform.assert_called_once()

    def test_status_under_review_sends_email(self):
        application = submit_franchise_application(
            applicant_name="Jane Smith",
            business_name="North Star Clubs",
            email="jane@example.com",
        )
        mail.outbox.clear()
        set_application_status(application, FranchiseApplication.Status.UNDER_REVIEW)
        assert len(mail.outbox) == 1
        assert "under review" in mail.outbox[0].subject.lower()
        application.refresh_from_db()
        assert application.status == FranchiseApplication.Status.UNDER_REVIEW

    def test_status_rejected_sends_email(self):
        application = submit_franchise_application(
            applicant_name="Jane Smith",
            business_name="North Star Clubs",
            email="jane@example.com",
        )
        mail.outbox.clear()
        set_application_status(application, FranchiseApplication.Status.REJECTED)
        assert len(mail.outbox) == 1
        application.refresh_from_db()
        assert application.status == FranchiseApplication.Status.REJECTED


@pytest.mark.django_db
class TestFranchiseAdminProvisioning:
    @patch(
        "franchises.services.create_franchise_admin_user", return_value=(MagicMock(), "secret-pass")
    )
    @patch("franchises.services.connections")
    @patch("franchises.services.call_command")
    @patch("franchises.services.register_franchise_database", return_value="franchise_admintest")
    def test_provision_with_admin_email(
        self, mock_register, mock_migrate, mock_connections, mock_create_admin
    ):
        franchise, password = provision_franchise(
            name="Test Franchise",
            slug="admintest",
            admin_email="admin@franchise.test",
            admin_name="Franchise Admin",
            seed=False,
        )
        mock_create_admin.assert_called_once()
        assert password == "secret-pass"
        assert franchise.slug == "admintest"

    @patch("franchises.services.set_franchise_context")
    def test_create_franchise_admin_user_role(self, mock_context):
        franchise = Franchise(
            name="Test",
            slug="rolecheck",
            database_alias="franchise_rolecheck",
        )
        with patch.object(User.objects, "using") as mock_using:
            mock_qs = mock_using.return_value
            mock_qs.filter.return_value.exists.return_value = False
            mock_user = MagicMock()
            mock_qs.create_user.return_value = mock_user

            _user, password = create_franchise_admin_user(
                franchise,
                email="lead@franchise.test",
                name="Lead Partner",
            )

            kwargs = mock_qs.create_user.call_args.kwargs
            assert kwargs["role"] == User.Role.FRANCHISE_ADMIN
            assert kwargs["email"] == "lead@franchise.test"
            assert password


class TestFranchiseApplicationViews(TestCase):
    def test_public_apply_page_loads(self):
        response = self.client.get(reverse("franchises:apply"))
        assert response.status_code == 200
        assert b"franchise partner" in response.content.lower()

    @patch("franchises.views.submit_franchise_application")
    def test_public_apply_submission_redirects(self, mock_submit):
        application = FranchiseApplication(
            reference="test-ref-123",
            applicant_name="Jane",
            business_name="Acme",
            proposed_slug="acme",
            email="jane@example.com",
        )
        mock_submit.return_value = application
        response = self.client.post(
            reverse("franchises:apply"),
            {
                "applicant_name": "Jane",
                "business_name": "Acme",
                "email": "jane@example.com",
                "phone": "",
                "region": "London",
                "experience_years": 5,
                "message": "Ready to launch",
            },
        )
        assert response.status_code == 302
        assert response.url.endswith("/franchise/apply/thanks/test-ref-123/")
