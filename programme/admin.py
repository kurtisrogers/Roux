from django.contrib import admin

from programme.models import Activity, Programme, ScheduleEvent, WeekPack, WeekPackBlock


class WeekPackBlockInline(admin.TabularInline):
    model = WeekPackBlock
    extra = 0


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ("name", "organisation", "category", "is_active")
    list_filter = ("category", "is_active")


@admin.register(WeekPack)
class WeekPackAdmin(admin.ModelAdmin):
    list_display = ("name", "organisation", "is_active")
    inlines = [WeekPackBlockInline]


@admin.register(Programme)
class ProgrammeAdmin(admin.ModelAdmin):
    list_display = ("name", "organisation", "session_type", "start_date", "end_date", "status")
    list_filter = ("status",)


@admin.register(ScheduleEvent)
class ScheduleEventAdmin(admin.ModelAdmin):
    list_display = ("kind", "organisation", "date", "start_date", "end_date", "programme")
    list_filter = ("kind",)
