from django.contrib import admin

from organisations.models import Organisation, Site, TermDate


class SiteInline(admin.TabularInline):
    model = Site
    extra = 0


class TermDateInline(admin.TabularInline):
    model = TermDate
    extra = 0


@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "city", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [SiteInline, TermDateInline]


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ("name", "organisation", "city", "capacity", "is_active")
    list_filter = ("organisation",)


@admin.register(TermDate)
class TermDateAdmin(admin.ModelAdmin):
    list_display = ("name", "organisation", "start_date", "end_date", "is_holiday")
