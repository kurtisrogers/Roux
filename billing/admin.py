from django.contrib import admin

from billing.models import Payment, Subscription


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("organisation", "amount", "status", "booking", "created_at")
    list_filter = ("status", "organisation")


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("organisation", "plan_name", "amount", "status")
