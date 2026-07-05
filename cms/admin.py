from django.contrib import admin

from cms.models import ContactSubmission, NavigationItem, Page, PageBlock, SiteSettings


class PageBlockInline(admin.TabularInline):
    model = PageBlock
    extra = 0


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ("title", "organisation", "slug", "is_published", "is_homepage")
    list_filter = ("organisation", "is_published")
    inlines = [PageBlockInline]


@admin.register(PageBlock)
class PageBlockAdmin(admin.ModelAdmin):
    list_display = ("page", "block_type", "order", "is_visible")


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ("organisation", "site_name", "contact_email")


@admin.register(NavigationItem)
class NavigationItemAdmin(admin.ModelAdmin):
    list_display = ("label", "organisation", "order", "is_visible")


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "organisation", "is_read", "created_at")
    list_filter = ("is_read",)
