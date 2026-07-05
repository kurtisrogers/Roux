from django import forms

from franchises.models import Franchise, FranchiseDomain


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
