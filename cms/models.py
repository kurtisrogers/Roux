from django.db import models


class SiteSettings(models.Model):
    organisation = models.OneToOneField(
        "organisations.Organisation",
        on_delete=models.CASCADE,
        related_name="site_settings",
    )
    site_name = models.CharField(max_length=200, blank=True)
    tagline = models.CharField(max_length=300, blank=True)
    logo = models.ImageField(upload_to="logos/", blank=True)
    primary_colour = models.CharField(max_length=7, default="#1a5fb4")
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    footer_text = models.TextField(blank=True)
    google_analytics_id = models.CharField(max_length=50, blank=True)

    def __str__(self) -> str:
        return f"Settings: {self.organisation.name}"


class NavigationItem(models.Model):
    organisation = models.ForeignKey(
        "organisations.Organisation",
        on_delete=models.CASCADE,
        related_name="nav_items",
    )
    label = models.CharField(max_length=100)
    page = models.ForeignKey(
        "cms.Page",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="nav_items",
    )
    external_url = models.URLField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]

    def __str__(self) -> str:
        return self.label

    @property
    def url(self) -> str:
        if self.page:
            if self.page.is_homepage:
                return "/"
            return f"/{self.page.slug}/"
        return self.external_url


class Page(models.Model):
    organisation = models.ForeignKey(
        "organisations.Organisation",
        on_delete=models.CASCADE,
        related_name="pages",
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    meta_description = models.CharField(max_length=300, blank=True)
    is_homepage = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    show_in_nav = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]
        unique_together = [["organisation", "slug"]]

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if self.is_homepage:
            Page.objects.filter(
                organisation=self.organisation,
                is_homepage=True,
            ).exclude(pk=self.pk).update(is_homepage=False)
        super().save(*args, **kwargs)


class PageBlock(models.Model):
    class BlockType(models.TextChoices):
        HERO = "hero", "Hero Banner"
        RICH_TEXT = "rich_text", "Rich Text"
        FEATURES = "features", "Feature Grid"
        CTA = "cta", "Call to Action"
        IMAGE_TEXT = "image_text", "Image & Text"
        CONTACT_FORM = "contact_form", "Contact Form"
        SESSION_LIST = "session_list", "Available Sessions"
        PRICING = "pricing", "Pricing Table"
        FAQ = "faq", "FAQ Accordion"
        TESTIMONIALS = "testimonials", "Testimonials"

    page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
        related_name="blocks",
    )
    block_type = models.CharField(max_length=20, choices=BlockType.choices)
    order = models.PositiveIntegerField(default=0)
    content = models.JSONField(default=dict)
    is_visible = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]

    def __str__(self) -> str:
        return f"{self.get_block_type_display()} on {self.page.title}"


class ContactSubmission(models.Model):
    organisation = models.ForeignKey(
        "organisations.Organisation",
        on_delete=models.CASCADE,
        related_name="contact_submissions",
    )
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Contact from {self.name}"
