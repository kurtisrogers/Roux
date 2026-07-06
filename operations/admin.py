from django.contrib import admin

from operations.models import (
    Absence,
    AuthorisedCollector,
    ChildcareVoucher,
    FranchiseOnboardingTask,
    MedicationAdministration,
    PaymentPlan,
    RecurringBooking,
    SafeguardingCase,
    StaffCompliance,
    StaffShift,
    SubsidyCode,
    Visitor,
    VoucherRedemption,
    WaitlistEntry,
)


@admin.register(RecurringBooking)
class RecurringBookingAdmin(admin.ModelAdmin):
    list_display = ("child", "session_type", "weekday", "is_active")
    list_filter = ("is_active", "weekday")


@admin.register(WaitlistEntry)
class WaitlistEntryAdmin(admin.ModelAdmin):
    list_display = ("child", "session", "position", "created_at")
    ordering = ("session", "position")


@admin.register(Absence)
class AbsenceAdmin(admin.ModelAdmin):
    list_display = ("child", "date", "session", "reported_by")
    list_filter = ("date",)


@admin.register(AuthorisedCollector)
class AuthorisedCollectorAdmin(admin.ModelAdmin):
    list_display = ("name", "child", "relationship", "is_primary", "is_active")


@admin.register(StaffShift)
class StaffShiftAdmin(admin.ModelAdmin):
    list_display = ("user", "site", "date", "start_time", "end_time")


@admin.register(MedicationAdministration)
class MedicationAdministrationAdmin(admin.ModelAdmin):
    list_display = ("child", "medication_name", "administered_at", "administered_by")


@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ("name", "site", "signed_in_at", "signed_out_at")


@admin.register(StaffCompliance)
class StaffComplianceAdmin(admin.ModelAdmin):
    list_display = ("user", "dbs_expiry", "first_aid_expiry")


@admin.register(SafeguardingCase)
class SafeguardingCaseAdmin(admin.ModelAdmin):
    list_display = ("title", "child", "status", "assigned_to")
    list_filter = ("status",)


@admin.register(SubsidyCode)
class SubsidyCodeAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "organisation", "is_active")


@admin.register(ChildcareVoucher)
class ChildcareVoucherAdmin(admin.ModelAdmin):
    list_display = ("reference", "parent", "provider", "balance", "is_active")


@admin.register(VoucherRedemption)
class VoucherRedemptionAdmin(admin.ModelAdmin):
    list_display = ("voucher", "booking", "amount", "redeemed_at")


@admin.register(PaymentPlan)
class PaymentPlanAdmin(admin.ModelAdmin):
    list_display = ("name", "child", "total_amount", "status")


@admin.register(FranchiseOnboardingTask)
class FranchiseOnboardingTaskAdmin(admin.ModelAdmin):
    list_display = ("franchise", "label", "completed_at")
