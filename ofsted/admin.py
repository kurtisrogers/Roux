from django.contrib import admin

from ofsted.models import Incident, OfstedReport, RatioCheck


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ("incident_type", "severity", "organisation", "occurred_at", "ofsted_notifiable")
    list_filter = ("incident_type", "severity", "ofsted_notifiable")


@admin.register(RatioCheck)
class RatioCheckAdmin(admin.ModelAdmin):
    list_display = (
        "session",
        "child_count",
        "staff_count",
        "required_staff",
        "compliant",
        "checked_at",
    )


@admin.register(OfstedReport)
class OfstedReportAdmin(admin.ModelAdmin):
    list_display = ("report_type", "organisation", "period_start", "period_end", "generated_at")
