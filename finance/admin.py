from django.contrib import admin

from finance.models import XeroConnection, XeroInvoice


@admin.register(XeroConnection)
class XeroConnectionAdmin(admin.ModelAdmin):
    list_display = ("organisation", "tenant_name", "is_connected", "auto_sync_invoices")


@admin.register(XeroInvoice)
class XeroInvoiceAdmin(admin.ModelAdmin):
    list_display = ("invoice_number", "organisation", "amount", "status", "last_synced_at")
    list_filter = ("status",)
