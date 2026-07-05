from django.contrib import admin

from bookings.models import Attendance, Booking, Child, Session, SessionType


@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    list_display = ("full_name", "parent", "organisation", "date_of_birth", "is_active")
    list_filter = ("organisation", "is_active")


@admin.register(SessionType)
class SessionTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "organisation", "category", "price", "capacity")


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ("session_type", "site", "date", "start_time", "status")
    list_filter = ("organisation", "status", "date")
    filter_horizontal = ("staff",)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("child", "session", "status", "payment_status", "created_at")
    list_filter = ("status", "payment_status")


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("booking", "checked_in_at", "checked_out_at")
