from decimal import Decimal

from django.db import models
from django.utils.text import slugify


class Organisation(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    county = models.CharField(max_length=100, blank=True)
    postcode = models.CharField(max_length=10, blank=True)
    ofsted_number = models.CharField(max_length=50, blank=True)
    stripe_customer_id = models.CharField(max_length=255, blank=True)
    sibling_discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("10"),
        help_text="Discount % when booking multiple children in one checkout",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            slug = base
            counter = 1
            while Organisation.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class Site(models.Model):
    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.CASCADE,
        related_name="sites",
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    postcode = models.CharField(max_length=10, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    capacity = models.PositiveIntegerField(default=30)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        unique_together = [["organisation", "slug"]]

    def __str__(self) -> str:
        return f"{self.name} ({self.organisation.name})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class TermDate(models.Model):
    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.CASCADE,
        related_name="term_dates",
    )
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    is_holiday = models.BooleanField(
        default=False,
        help_text="Holiday periods when wraparound care may be unavailable.",
    )

    class Meta:
        ordering = ["start_date"]

    def __str__(self) -> str:
        return f"{self.name} ({self.start_date} – {self.end_date})"
