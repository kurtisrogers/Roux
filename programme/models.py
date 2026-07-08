from django.core.exceptions import ValidationError
from django.db import models


class Weekday(models.IntegerChoices):
    MONDAY = 0, "Monday"
    TUESDAY = 1, "Tuesday"
    WEDNESDAY = 2, "Wednesday"
    THURSDAY = 3, "Thursday"
    FRIDAY = 4, "Friday"
    SATURDAY = 5, "Saturday"
    SUNDAY = 6, "Sunday"


class Activity(models.Model):
    class Category(models.TextChoices):
        SPORT = "sport", "Sport"
        CREATIVE = "creative", "Creative"
        QUIET = "quiet", "Quiet / homework"
        OUTDOOR = "outdoor", "Outdoor"
        FOOD = "food", "Food / snack"
        OTHER = "other", "Other"

    organisation = models.ForeignKey(
        "organisations.Organisation",
        on_delete=models.CASCADE,
        related_name="activities",
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.OTHER,
    )
    default_duration_minutes = models.PositiveIntegerField(default=30)
    resources = models.TextField(blank=True, help_text="Equipment, room, etc.")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "activities"

    def __str__(self) -> str:
        return self.name


class WeekPack(models.Model):
    organisation = models.ForeignKey(
        "organisations.Organisation",
        on_delete=models.CASCADE,
        related_name="week_packs",
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class WeekPackBlock(models.Model):
    week_pack = models.ForeignKey(
        WeekPack,
        on_delete=models.CASCADE,
        related_name="blocks",
    )
    weekday = models.IntegerField(choices=Weekday.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    activity = models.ForeignKey(
        Activity,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="week_pack_blocks",
    )
    label = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_running_period = models.BooleanField(
        default=True,
        help_text="Uncheck for snack, break, or handover slots.",
    )

    class Meta:
        ordering = ["weekday", "sort_order", "start_time"]
        unique_together = [["week_pack", "weekday", "start_time"]]

    def __str__(self) -> str:
        title = self.label or (self.activity.name if self.activity else "Break")
        return f"{self.get_weekday_display()} {self.start_time:%H:%M} – {title}"

    def clean(self) -> None:
        if self.end_time <= self.start_time:
            raise ValidationError({"end_time": "End time must be after start time."})


class Programme(models.Model):
    class FirstWeek(models.TextChoices):
        A = "A", "Week A"
        B = "B", "Week B"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"

    organisation = models.ForeignKey(
        "organisations.Organisation",
        on_delete=models.CASCADE,
        related_name="programmes",
    )
    site = models.ForeignKey(
        "organisations.Site",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="programmes",
        help_text="Leave blank to apply to all sites.",
    )
    session_type = models.ForeignKey(
        "bookings.SessionType",
        on_delete=models.CASCADE,
        related_name="programmes",
    )
    name = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()
    week_a_pack = models.ForeignKey(
        WeekPack,
        on_delete=models.PROTECT,
        related_name="programmes_as_week_a",
    )
    week_b_pack = models.ForeignKey(
        WeekPack,
        on_delete=models.PROTECT,
        related_name="programmes_as_week_b",
    )
    anchor_date = models.DateField(
        help_text="Reference date for Week A/B alternation (usually term start).",
    )
    first_week = models.CharField(
        max_length=1,
        choices=FirstWeek.choices,
        default=FirstWeek.A,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self) -> str:
        return self.name

    def clean(self) -> None:
        if self.end_date < self.start_date:
            raise ValidationError({"end_date": "End date must be on or after start date."})
        if self.week_a_pack.organisation_id != self.organisation_id:
            raise ValidationError({"week_a_pack": "Week A pack must belong to this organisation."})
        if self.week_b_pack.organisation_id != self.organisation_id:
            raise ValidationError({"week_b_pack": "Week B pack must belong to this organisation."})
        if self.status == self.Status.PUBLISHED:
            overlap = Programme.objects.filter(
                organisation=self.organisation,
                session_type=self.session_type,
                status=self.Status.PUBLISHED,
                start_date__lte=self.end_date,
                end_date__gte=self.start_date,
            )
            if self.site_id:
                overlap = overlap.filter(models.Q(site=self.site) | models.Q(site__isnull=True))
            else:
                overlap = overlap.filter(models.Q(site__isnull=True) | models.Q(site__isnull=False))
            if self.pk:
                overlap = overlap.exclude(pk=self.pk)
            if overlap.exists():
                raise ValidationError(
                    "Another published programme overlaps this date range for the same session type."
                )


class ScheduleEvent(models.Model):
    class Kind(models.TextChoices):
        SINGLE = "single", "Single day"
        CLOSURE = "closure", "Closure / non-running"

    programme = models.ForeignKey(
        Programme,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="schedule_events",
    )
    organisation = models.ForeignKey(
        "organisations.Organisation",
        on_delete=models.CASCADE,
        related_name="schedule_events",
    )
    kind = models.CharField(max_length=20, choices=Kind.choices)
    site = models.ForeignKey(
        "organisations.Site",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="schedule_events",
    )
    session_type = models.ForeignKey(
        "bookings.SessionType",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="schedule_events",
    )
    date = models.DateField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    activity = models.ForeignKey(
        Activity,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="schedule_events",
    )
    label = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    replaces_day = models.BooleanField(
        default=False,
        help_text="For single-day events: replace the whole day instead of merging.",
    )
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date", "start_date", "sort_order", "start_time"]

    def __str__(self) -> str:
        if self.kind == self.Kind.CLOSURE:
            return f"Closure {self.start_date} – {self.end_date}"
        return f"{self.date}: {self.label or self.activity}"

    def clean(self) -> None:
        if self.kind == self.Kind.SINGLE:
            if not self.date:
                raise ValidationError({"date": "Required for single-day events."})
            if self.start_time and self.end_time and self.end_time <= self.start_time:
                raise ValidationError({"end_time": "End time must be after start time."})
        elif self.kind == self.Kind.CLOSURE:
            if not self.start_date or not self.end_date:
                raise ValidationError("Closure requires start and end dates.")
            if self.end_date < self.start_date:
                raise ValidationError({"end_date": "End date must be on or after start date."})
