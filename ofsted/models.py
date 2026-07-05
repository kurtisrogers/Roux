from django.conf import settings
from django.db import models


class Incident(models.Model):
    class Type(models.TextChoices):
        ACCIDENT = "accident", "Accident / Injury"
        SAFEGUARDING = "safeguarding", "Safeguarding Concern"
        BEHAVIOUR = "behaviour", "Behaviour Incident"
        MEDICATION = "medication", "Medication Administered"
        OTHER = "other", "Other"

    class Severity(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    organisation = models.ForeignKey(
        "organisations.Organisation",
        on_delete=models.CASCADE,
        related_name="incidents",
    )
    session = models.ForeignKey(
        "bookings.Session",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="incidents",
    )
    child = models.ForeignKey(
        "bookings.Child",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="incidents",
    )
    incident_type = models.CharField(max_length=20, choices=Type.choices)
    severity = models.CharField(
        max_length=20,
        choices=Severity.choices,
        default=Severity.LOW,
    )
    occurred_at = models.DateTimeField()
    location = models.CharField(max_length=200, blank=True)
    description = models.TextField()
    action_taken = models.TextField(blank=True)
    parent_notified = models.BooleanField(default=False)
    parent_notified_at = models.DateTimeField(null=True, blank=True)
    ofsted_notifiable = models.BooleanField(
        default=False,
        help_text="Mark if this incident must be reported to Ofsted.",
    )
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="incidents_reported",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-occurred_at"]

    def __str__(self) -> str:
        return f"{self.get_incident_type_display()} – {self.occurred_at.date()}"


class RatioCheck(models.Model):
    session = models.ForeignKey(
        "bookings.Session",
        on_delete=models.CASCADE,
        related_name="ratio_checks",
    )
    checked_at = models.DateTimeField(auto_now_add=True)
    checked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
    )
    child_count = models.PositiveIntegerField()
    staff_count = models.PositiveIntegerField()
    required_staff = models.PositiveIntegerField()
    compliant = models.BooleanField()
    age_groups = models.JSONField(default=dict)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-checked_at"]

    def __str__(self) -> str:
        status = "OK" if self.compliant else "NON-COMPLIANT"
        return f"Ratio check {self.session} – {status}"


class OfstedReport(models.Model):
    class ReportType(models.TextChoices):
        MONTHLY = "monthly", "Monthly Summary"
        INCIDENT = "incident", "Incident Report"
        RATIO = "ratio", "Ratio Compliance"
        ANNUAL = "annual", "Annual Return"

    organisation = models.ForeignKey(
        "organisations.Organisation",
        on_delete=models.CASCADE,
        related_name="ofsted_reports",
    )
    report_type = models.CharField(max_length=20, choices=ReportType.choices)
    period_start = models.DateField()
    period_end = models.DateField()
    generated_at = models.DateTimeField(auto_now_add=True)
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
    )
    data = models.JSONField(default=dict)
    file = models.FileField(upload_to="ofsted_reports/", blank=True)

    class Meta:
        ordering = ["-generated_at"]

    def __str__(self) -> str:
        return f"{self.get_report_type_display()} ({self.period_start} – {self.period_end})"
