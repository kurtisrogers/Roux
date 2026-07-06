from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class RecurringBooking(models.Model):
    """Standing booking pattern — e.g. every Tuesday after-school."""

    class Weekday(models.IntegerChoices):
        MONDAY = 0, "Monday"
        TUESDAY = 1, "Tuesday"
        WEDNESDAY = 2, "Wednesday"
        THURSDAY = 3, "Thursday"
        FRIDAY = 4, "Friday"
        SATURDAY = 5, "Saturday"
        SUNDAY = 6, "Sunday"

    child = models.ForeignKey(
        "bookings.Child",
        on_delete=models.CASCADE,
        related_name="recurring_bookings",
    )
    session_type = models.ForeignKey(
        "bookings.SessionType",
        on_delete=models.CASCADE,
        related_name="recurring_bookings",
    )
    site = models.ForeignKey(
        "organisations.Site",
        on_delete=models.CASCADE,
        related_name="recurring_bookings",
    )
    weekday = models.IntegerField(choices=Weekday.choices)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["child__last_name", "weekday"]

    def __str__(self) -> str:
        return f"{self.child} – {self.get_weekday_display()} {self.session_type.name}"


class WaitlistEntry(models.Model):
    child = models.ForeignKey(
        "bookings.Child",
        on_delete=models.CASCADE,
        related_name="waitlist_entries",
    )
    session = models.ForeignKey(
        "bookings.Session",
        on_delete=models.CASCADE,
        related_name="waitlist_entries",
    )
    position = models.PositiveIntegerField(default=1)
    notified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["session", "position"]
        unique_together = [["child", "session"]]

    def __str__(self) -> str:
        return f"Waitlist #{self.position}: {self.child} → {self.session}"


class Absence(models.Model):
    child = models.ForeignKey(
        "bookings.Child",
        on_delete=models.CASCADE,
        related_name="absences",
    )
    session = models.ForeignKey(
        "bookings.Session",
        on_delete=models.CASCADE,
        related_name="absences",
        null=True,
        blank=True,
    )
    date = models.DateField()
    reason = models.TextField(blank=True)
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="absences_reported",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]
        unique_together = [["child", "date", "session"]]

    def __str__(self) -> str:
        return f"Absence: {self.child} on {self.date}"


class AuthorisedCollector(models.Model):
    child = models.ForeignKey(
        "bookings.Child",
        on_delete=models.CASCADE,
        related_name="authorised_collectors",
    )
    name = models.CharField(max_length=200)
    relationship = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    pin_code = models.CharField(max_length=10, blank=True, help_text="Optional collection PIN")
    is_primary = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-is_primary", "name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.child})"


class StaffShift(models.Model):
    """Staff rota entry."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="shifts",
    )
    site = models.ForeignKey(
        "organisations.Site",
        on_delete=models.CASCADE,
        related_name="shifts",
    )
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["date", "start_time"]

    def __str__(self) -> str:
        return f"{self.user} @ {self.site} {self.date}"


class MedicationAdministration(models.Model):
    child = models.ForeignKey(
        "bookings.Child",
        on_delete=models.CASCADE,
        related_name="medication_logs",
    )
    session = models.ForeignKey(
        "bookings.Session",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="medication_logs",
    )
    medication_name = models.CharField(max_length=200)
    dose = models.CharField(max_length=100)
    administered_at = models.DateTimeField()
    administered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="medications_administered",
    )
    witnessed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="medications_witnessed",
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-administered_at"]

    def __str__(self) -> str:
        return f"{self.medication_name} – {self.child}"


class Visitor(models.Model):
    site = models.ForeignKey(
        "organisations.Site",
        on_delete=models.CASCADE,
        related_name="visitors",
    )
    name = models.CharField(max_length=200)
    organisation_name = models.CharField(max_length=200, blank=True)
    purpose = models.CharField(max_length=255)
    signed_in_at = models.DateTimeField()
    signed_out_at = models.DateTimeField(null=True, blank=True)
    dbs_checked = models.BooleanField(default=False)
    signed_in_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="visitors_signed_in",
    )

    class Meta:
        ordering = ["-signed_in_at"]

    def __str__(self) -> str:
        return f"{self.name} @ {self.site}"


class StaffCompliance(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="compliance",
    )
    dbs_number = models.CharField(max_length=50, blank=True)
    dbs_expiry = models.DateField(null=True, blank=True)
    first_aid_expiry = models.DateField(null=True, blank=True)
    safeguarding_expiry = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self) -> str:
        return f"Compliance: {self.user}"


class SafeguardingCase(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        INVESTIGATING = "investigating", "Investigating"
        REFERRED = "referred", "Referred to authority"
        CLOSED = "closed", "Closed"

    organisation = models.ForeignKey(
        "organisations.Organisation",
        on_delete=models.CASCADE,
        related_name="safeguarding_cases",
    )
    child = models.ForeignKey(
        "bookings.Child",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="safeguarding_cases",
    )
    incident = models.ForeignKey(
        "ofsted.Incident",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="safeguarding_cases",
    )
    title = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="safeguarding_cases_assigned",
    )
    escalated_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title


class SubsidyCode(models.Model):
    organisation = models.ForeignKey(
        "organisations.Organisation",
        on_delete=models.CASCADE,
        related_name="subsidy_codes",
    )
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=200)
    local_authority = models.CharField(max_length=200, blank=True)
    discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("100"))],
    )
    fixed_discount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal("0"),
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = [["organisation", "code"]]
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.code} – {self.name}"


class ChildcareVoucher(models.Model):
    """Employer childcare voucher account (Edenred, Sodexo, etc.)."""

    class Provider(models.TextChoices):
        EDENRED = "edenred", "Edenred"
        SODEXO = "sodexo", "Sodexo"
        COMPUTERSHARE = "computershare", "Computershare"
        OTHER = "other", "Other"

    organisation = models.ForeignKey(
        "organisations.Organisation",
        on_delete=models.CASCADE,
        related_name="childcare_vouchers",
    )
    parent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="childcare_vouchers",
    )
    child = models.ForeignKey(
        "bookings.Child",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="childcare_vouchers",
    )
    provider = models.CharField(max_length=20, choices=Provider.choices, default=Provider.OTHER)
    reference = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.get_provider_display()} {self.reference}"


class VoucherRedemption(models.Model):
    voucher = models.ForeignKey(
        ChildcareVoucher,
        on_delete=models.CASCADE,
        related_name="redemptions",
    )
    booking = models.ForeignKey(
        "bookings.Booking",
        on_delete=models.CASCADE,
        related_name="voucher_redemptions",
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    redeemed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"£{self.amount} voucher → {self.booking}"


class PaymentPlan(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    organisation = models.ForeignKey(
        "organisations.Organisation",
        on_delete=models.CASCADE,
        related_name="payment_plans",
    )
    child = models.ForeignKey(
        "bookings.Child",
        on_delete=models.CASCADE,
        related_name="payment_plans",
    )
    name = models.CharField(max_length=200)
    term_start = models.DateField()
    term_end = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    installments = models.PositiveSmallIntegerField(default=1)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        ordering = ["-term_start"]

    def __str__(self) -> str:
        return f"{self.name} – {self.child}"


class FranchiseOnboardingTask(models.Model):
    franchise = models.ForeignKey(
        "franchises.Franchise",
        on_delete=models.CASCADE,
        related_name="onboarding_tasks",
    )
    task_key = models.CharField(max_length=50)
    label = models.CharField(max_length=200)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = [["franchise", "task_key"]]
        ordering = ["task_key"]

    def __str__(self) -> str:
        return f"{self.franchise.slug}: {self.label}"
