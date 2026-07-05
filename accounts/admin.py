from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from accounts.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "role", "organisation", "is_active")
    list_filter = ("role", "organisation", "is_active")
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Roux", {"fields": ("role", "phone", "organisation", "site")}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Roux", {"fields": ("role", "phone", "organisation", "site")}),
    )
