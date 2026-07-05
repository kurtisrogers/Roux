from django.db import models


class XeroConnection(models.Model):
    organisation = models.OneToOneField(
        "organisations.Organisation",
        on_delete=models.CASCADE,
        related_name="xero_connection",
    )
    tenant_id = models.CharField(max_length=255, blank=True)
    tenant_name = models.CharField(max_length=255, blank=True)
    access_token = models.TextField(blank=True)
    refresh_token = models.TextField(blank=True)
    token_expires_at = models.DateTimeField(null=True, blank=True)
    is_connected = models.BooleanField(default=False)
    auto_sync_invoices = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        status = "Connected" if self.is_connected else "Disconnected"
        return f"Xero ({self.organisation.name}) – {status}"


class XeroInvoice(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SUBMITTED = "submitted", "Submitted"
        AUTHORISED = "authorised", "Authorised"
        PAID = "paid", "Paid"
        VOIDED = "voided", "Voided"
        ERROR = "error", "Error"

    organisation = models.ForeignKey(
        "organisations.Organisation",
        on_delete=models.CASCADE,
        related_name="xero_invoices",
    )
    payment = models.OneToOneField(
        "billing.Payment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="xero_invoice",
    )
    booking = models.ForeignKey(
        "bookings.Booking",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="xero_invoices",
    )
    xero_invoice_id = models.CharField(max_length=255, blank=True)
    invoice_number = models.CharField(max_length=50, blank=True)
    contact_name = models.CharField(max_length=200, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    sync_error = models.TextField(blank=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Invoice {self.invoice_number or self.pk}"
