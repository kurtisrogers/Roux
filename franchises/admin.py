from django.contrib import admin

from franchises.models import Franchise, FranchiseApplication, FranchiseDomain


class FranchiseDomainInline(admin.TabularInline):
    model = FranchiseDomain
    extra = 0


@admin.register(Franchise)
class FranchiseAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "status", "database_alias", "contact_email")
    list_filter = ("status",)
    prepopulated_fields = {"slug": ("name",)}
    inlines = [FranchiseDomainInline]


@admin.register(FranchiseDomain)
class FranchiseDomainAdmin(admin.ModelAdmin):
    list_display = ("hostname", "franchise", "is_primary")


@admin.register(FranchiseApplication)
class FranchiseApplicationAdmin(admin.ModelAdmin):
    list_display = ("business_name", "applicant_name", "status", "email", "created_at")
    list_filter = ("status",)
    search_fields = ("business_name", "applicant_name", "email", "reference")
