from django.db import models
from django.utils.text import slugify


class Franchise(models.Model):
    """Control-plane record for an isolated franchise tenant."""

    class Status(models.TextChoices):
        PROVISIONING = "provisioning", "Provisioning"
        ACTIVE = "active", "Active"
        SUSPENDED = "suspended", "Suspended"
        ARCHIVED = "archived", "Archived"

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=100, unique=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PROVISIONING,
    )
    database_alias = models.CharField(
        max_length=100,
        unique=True,
        help_text="Django DATABASES alias for this franchise.",
    )
    database_url = models.TextField(
        blank=True,
        help_text="PostgreSQL URL for production. Empty uses SQLite file in dev.",
    )
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    # Per-franchise integrations (each franchise runs its own Stripe/Xero accounts)
    stripe_publishable_key = models.CharField(max_length=255, blank=True)
    stripe_secret_key = models.CharField(max_length=255, blank=True)
    stripe_webhook_secret = models.CharField(max_length=255, blank=True)
    stripe_connect_account_id = models.CharField(
        max_length=255,
        blank=True,
        help_text="Optional Stripe Connect account ID.",
    )
    xero_client_id = models.CharField(max_length=255, blank=True)
    xero_client_secret = models.CharField(max_length=255, blank=True)
    xero_redirect_uri = models.URLField(blank=True)
    default_from_email = models.EmailField(blank=True)
    platform_fee_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Optional platform fee % taken by franchisor on payments.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.database_alias:
            self.database_alias = f"franchise_{self.slug}"
        super().save(*args, **kwargs)

    @property
    def is_active(self) -> bool:
        return self.status == self.Status.ACTIVE


class FranchiseDomain(models.Model):
    """Maps hostnames to a franchise for routing."""

    franchise = models.ForeignKey(
        Franchise,
        on_delete=models.CASCADE,
        related_name="domains",
    )
    hostname = models.CharField(
        max_length=255,
        unique=True,
        help_text="e.g. acme.roux.care or acme.localhost",
    )
    is_primary = models.BooleanField(default=False)

    class Meta:
        ordering = ["hostname"]

    def __str__(self) -> str:
        return self.hostname


class FranchiseApplication(models.Model):
    """Prospective franchisee application (control plane)."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        UNDER_REVIEW = "under_review", "Under Review"
        PARTNER = "partner", "Partner"
        REJECTED = "rejected", "Rejected"

    reference = models.CharField(max_length=32, unique=True, editable=False)
    applicant_name = models.CharField(max_length=200)
    business_name = models.CharField(max_length=200)
    proposed_slug = models.SlugField(max_length=100, unique=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    region = models.CharField(
        max_length=100,
        blank=True,
        help_text="UK region or area of operation",
    )
    experience_years = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Years of wraparound/childcare experience",
    )
    message = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    franchise = models.OneToOneField(
        Franchise,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="application",
    )
    admin_notes = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.business_name} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        if not self.proposed_slug:
            self.proposed_slug = slugify(self.business_name)
        super().save(*args, **kwargs)
