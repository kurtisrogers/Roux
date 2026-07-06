from django import forms

from franchises.models import Franchise, FranchiseApplication


class FranchiseApplicationForm(forms.ModelForm):
    class Meta:
        model = FranchiseApplication
        fields = (
            "applicant_name",
            "business_name",
            "email",
            "phone",
            "region",
            "experience_years",
            "message",
        )
        widgets = {
            "message": forms.Textarea(attrs={"rows": 4}),
            "experience_years": forms.NumberInput(attrs={"min": 0, "max": 50}),
        }


class FranchiseApplicationReviewForm(forms.ModelForm):
    class Meta:
        model = FranchiseApplication
        fields = ("status", "admin_notes")
        widgets = {
            "admin_notes": forms.Textarea(attrs={"rows": 3}),
        }


class FranchiseForm(forms.ModelForm):
    hostname = forms.CharField(
        max_length=255,
        required=False,
        help_text="Primary domain, e.g. acme.localhost or acme.roux.care",
    )

    class Meta:
        model = Franchise
        fields = (
            "name",
            "slug",
            "contact_email",
            "contact_phone",
            "stripe_publishable_key",
            "stripe_secret_key",
            "stripe_webhook_secret",
            "stripe_connect_account_id",
            "xero_client_id",
            "xero_client_secret",
            "xero_redirect_uri",
            "default_from_email",
            "platform_fee_percent",
        )


class FranchiseIntegrationForm(forms.ModelForm):
    class Meta:
        model = Franchise
        fields = (
            "stripe_publishable_key",
            "stripe_secret_key",
            "stripe_webhook_secret",
            "stripe_connect_account_id",
            "xero_client_id",
            "xero_client_secret",
            "xero_redirect_uri",
            "default_from_email",
        )
