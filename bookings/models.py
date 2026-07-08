from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Child(models.Model):
    parent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="children",
    )
    organisation = models.ForeignKey(
        "organisations.Organisation",
        on_delete=models.CASCADE,
        related_name="children",
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    school_year = models.CharField(max_length=20, blank=True)
    allergies = models.TextField(blank=True)
    medical_notes = models.TextField(blank=True)
    dietary_requirements = models.TextField(blank=True)
    emergency_contact_name = models.CharField(max_length=200)
    emergency_contact_phone = models.CharField(max_length=20)
    emergency_contact_relationship = models.CharField(max_length=100, blank=True)
    photo_consent = models.BooleanField(default=False)
    pupil_premium = models.BooleanField(default=False)
    fsm_eligible = models.BooleanField(
        default=False,
        verbose_name="Free school meals eligible",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["last_name", "first_name"]
        verbose_name_plural = "children"

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self) -> int:
        today = timezone.now().date()
        return (
            today.year
            - self.date_of_birth.year
            - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        )


class SessionType(models.Model):
    class Category(models.TextChoices):
        BREAKFAST = "breakfast", "Breakfast Club"
        AFTER_SCHOOL = "after_school", "After School Club"
        HOLIDAY = "holiday", "Holiday Club"
        OTHER = "other", "Other"

    organisation = models.ForeignKey(
        "organisations.Organisation",
        on_delete=models.CASCADE,
        related_name="session_types",
    )
    name = models.CharField(max_length=200)
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.AFTER_SCHOOL,
    )
    description = models.TextField(blank=True)
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    capacity = models.PositiveIntegerField(default=20)
    age_min = models.PositiveIntegerField(default=4)
    age_max = models.PositiveIntegerField(default=11)
    duration_minutes = models.PositiveIntegerField(default=60)
    late_pickup_fee = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal("5.00"),
        help_text="Fee per 15 minutes after grace period",
    )
    late_pickup_grace_minutes = models.PositiveIntegerField(default=15)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Session(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    organisation = models.ForeignKey(
        "organisations.Organisation",
        on_delete=models.CASCADE,
        related_name="sessions",
    )
    site = models.ForeignKey(
        "organisations.Site",
        on_delete=models.CASCADE,
        related_name="sessions",
    )
    session_type = models.ForeignKey(
        SessionType,
        on_delete=models.PROTECT,
        related_name="sessions",
    )
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SCHEDULED,
    )
    staff = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="assigned_sessions",
    )
    notes = models.TextField(blank=True)
    register_notes = models.TextField(blank=True)
    register_closed_at = models.DateTimeField(null=True, blank=True)
    register_closed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="registers_closed",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date", "start_time"]
        unique_together = [["site", "session_type", "date", "start_time"]]

    def __str__(self) -> str:
        return f"{self.session_type.name} – {self.date}"

    @property
    def booked_count(self) -> int:
        return self.bookings.filter(
            status__in=[Booking.Status.CONFIRMED, Booking.Status.CHECKED_IN]
        ).count()

    @property
    def spaces_remaining(self) -> int:
        return max(0, self.session_type.capacity - self.booked_count)

    @property
    def is_full(self) -> bool:
        return self.spaces_remaining == 0


class Booking(models.Model):
    class Source(models.TextChoices):
        ONLINE = "online", "Online"
        WALK_IN = "walk_in", "Walk-in"
        RECURRING = "recurring", "Recurring"
        WAITLIST = "waitlist", "Waitlist"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        CHECKED_IN = "checked_in", "Checked In"
        CHECKED_OUT = "checked_out", "Checked Out"
        CANCELLED = "cancelled", "Cancelled"
        NO_SHOW = "no_show", "No Show"

    class PaymentStatus(models.TextChoices):
        UNPAID = "unpaid", "Unpaid"
        PENDING = "pending", "Payment Pending"
        PAID = "paid", "Paid"
        REFUNDED = "refunded", "Refunded"
        WAIVED = "waived", "Waived"

    child = models.ForeignKey(
        Child,
        on_delete=models.CASCADE,
        related_name="bookings",
    )
    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
        related_name="bookings",
    )
    booked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="bookings_made",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.UNPAID,
    )
    special_requirements = models.TextField(blank=True)
    source = models.CharField(
        max_length=20,
        choices=Source.choices,
        default=Source.ONLINE,
    )
    subsidy_code = models.ForeignKey(
        "operations.SubsidyCode",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bookings",
    )
    late_fee_amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal("0"),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = [["child", "session"]]

    def __str__(self) -> str:
        return f"{self.child} → {self.session}"

    @property
    def price(self):
        return self.session.session_type.price


class Attendance(models.Model):
    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name="attendance",
    )
    checked_in_at = models.DateTimeField(null=True, blank=True)
    checked_in_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="check_ins",
    )
    checked_out_at = models.DateTimeField(null=True, blank=True)
    checked_out_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="check_outs",
    )
    collected_by = models.ForeignKey(
        "operations.AuthorisedCollector",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="collections",
    )
    collection_verified_name = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self) -> str:
        return f"Attendance: {self.booking}"
