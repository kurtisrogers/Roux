import calendar
from datetime import date, timedelta

from accounts.decorators import dashboard_required, role_required
from accounts.models import User
from bookings.models import SessionType
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from organisations.models import Site
from programme.forms import (
    ActivityForm,
    DayOverrideForm,
    ProgrammeForm,
    ScheduleEventClosureForm,
    WeekPackBlockForm,
    WeekPackForm,
)
from programme.models import Activity, Programme, ScheduleEvent, WeekPack, WeekPackBlock
from programme.services import (
    duplicate_week_pack,
    publish_programme,
    resolve_programme,
    week_label_for_date,
)

from dashboard.mixins import dashboard_context
from dashboard.views import _org_or_403


def _prog_ctx(request, org, title: str, **extra):
    return {**dashboard_context(request, org), "title": title, **extra}


def _staff_roles():
    return (
        User.Role.SUPER_ADMIN,
        User.Role.ORG_ADMIN,
        User.Role.SITE_MANAGER,
        User.Role.STAFF,
    )


def _manager_roles():
    return (User.Role.SUPER_ADMIN, User.Role.ORG_ADMIN, User.Role.SITE_MANAGER)


# --- Activities ---


@dashboard_required
@role_required(*_manager_roles())
def activity_list(request):
    org = _org_or_403(request)
    activities = Activity.objects.filter(organisation=org).order_by("name")
    form = ActivityForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        activity = form.save(commit=False)
        activity.organisation = org
        activity.save()
        messages.success(request, f"Activity “{activity.name}” saved.")
        return redirect("dashboard:activity_list")
    return render(
        request,
        "dashboard/programme/activities.html",
        _prog_ctx(request, org, "Activities", activities=activities, form=form),
    )


@dashboard_required
@role_required(*_manager_roles())
def activity_edit(request, pk):
    org = _org_or_403(request)
    activity = get_object_or_404(Activity, pk=pk, organisation=org)
    form = ActivityForm(request.POST or None, instance=activity)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Activity updated.")
        return redirect("dashboard:activity_list")
    return render(
        request,
        "dashboard/programme/activity_form.html",
        _prog_ctx(request, org, "Edit activity", form=form, activity=activity),
    )


# --- Week packs ---


@dashboard_required
@role_required(*_manager_roles())
def week_pack_list(request):
    org = _org_or_403(request)
    packs = WeekPack.objects.filter(organisation=org).prefetch_related("blocks")
    form = WeekPackForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        pack = form.save(commit=False)
        pack.organisation = org
        pack.save()
        messages.success(request, f"Week pack “{pack.name}” created.")
        return redirect("dashboard:week_pack_detail", pk=pack.pk)
    return render(
        request,
        "dashboard/programme/week_packs.html",
        _prog_ctx(request, org, "Week packs", packs=packs, form=form),
    )


@dashboard_required
@role_required(*_manager_roles())
def week_pack_detail(request, pk):
    org = _org_or_403(request)
    pack = get_object_or_404(WeekPack, pk=pk, organisation=org)
    form = WeekPackBlockForm(request.POST or None)
    form.fields["activity"].queryset = Activity.objects.filter(organisation=org, is_active=True)
    if request.method == "POST" and form.is_valid():
        block = form.save(commit=False)
        block.week_pack = pack
        block.save()
        messages.success(request, "Block added.")
        return redirect("dashboard:week_pack_detail", pk=pack.pk)
    blocks = pack.blocks.select_related("activity").all()
    weekday_columns = []
    for day_value, day_label in WeekPackBlock._meta.get_field("weekday").choices:
        weekday_columns.append((day_label, [b for b in blocks if b.weekday == day_value]))
    return render(
        request,
        "dashboard/programme/week_pack_detail.html",
        _prog_ctx(
            request,
            org,
            pack.name,
            pack=pack,
            form=form,
            weekday_columns=weekday_columns,
        ),
    )


@dashboard_required
@role_required(*_manager_roles())
@require_POST
def week_pack_duplicate(request, pk):
    org = _org_or_403(request)
    pack = get_object_or_404(WeekPack, pk=pk, organisation=org)
    new_name = request.POST.get("name", f"{pack.name} (copy)")
    duplicate = duplicate_week_pack(pack, new_name)
    messages.success(request, f"Duplicated as “{duplicate.name}”.")
    return redirect("dashboard:week_pack_detail", pk=duplicate.pk)


@dashboard_required
@role_required(*_manager_roles())
@require_POST
def week_pack_block_delete(request, pk):
    org = _org_or_403(request)
    block = get_object_or_404(WeekPackBlock, pk=pk, week_pack__organisation=org)
    pack_pk = block.week_pack_id
    block.delete()
    messages.success(request, "Block removed.")
    return redirect("dashboard:week_pack_detail", pk=pack_pk)


# --- Programmes ---


@dashboard_required
@role_required(*_manager_roles())
def programme_list(request):
    org = _org_or_403(request)
    programmes = Programme.objects.filter(organisation=org).select_related(
        "session_type", "site", "week_a_pack", "week_b_pack"
    )
    return render(
        request,
        "dashboard/programme/programmes.html",
        _prog_ctx(request, org, "Programmes", programmes=programmes),
    )


@dashboard_required
@role_required(*_manager_roles())
def programme_create(request):
    org = _org_or_403(request)
    form = ProgrammeForm(request.POST or None)
    form.fields["site"].queryset = Site.objects.filter(organisation=org)
    form.fields["session_type"].queryset = SessionType.objects.filter(
        organisation=org, is_active=True
    )
    form.fields["week_a_pack"].queryset = WeekPack.objects.filter(organisation=org, is_active=True)
    form.fields["week_b_pack"].queryset = WeekPack.objects.filter(organisation=org, is_active=True)
    if request.method == "POST" and form.is_valid():
        programme = form.save(commit=False)
        programme.organisation = org
        programme.save()
        messages.success(request, "Programme created as draft.")
        return redirect("dashboard:programme_detail", pk=programme.pk)
    return render(
        request,
        "dashboard/programme/programme_form.html",
        _prog_ctx(request, org, "New programme", form=form),
    )


@dashboard_required
@role_required(*_manager_roles())
def programme_detail(request, pk):
    org = _org_or_403(request)
    programme = get_object_or_404(
        Programme.objects.select_related("week_a_pack", "week_b_pack", "session_type", "site"),
        pk=pk,
        organisation=org,
    )
    preview = []
    current = programme.start_date
    for _ in range(28):
        if current > programme.end_date:
            break
        if current.weekday() < 5:
            blocks = resolve_programme(programme, current)
            preview.append(
                {
                    "date": current,
                    "week_label": week_label_for_date(programme, current),
                    "blocks": blocks,
                    "closed": blocks is None and current >= programme.start_date,
                }
            )
        current += timedelta(days=1)
    return render(
        request,
        "dashboard/programme/programme_detail.html",
        _prog_ctx(request, org, programme.name, programme=programme, preview=preview[:14]),
    )


@dashboard_required
@role_required(*_manager_roles())
@require_POST
def programme_publish(request, pk):
    org = _org_or_403(request)
    programme = get_object_or_404(Programme, pk=pk, organisation=org)
    try:
        publish_programme(programme)
        messages.success(request, "Programme published.")
    except ValidationError as exc:
        messages.error(request, "; ".join(exc.messages))
    return redirect("dashboard:programme_detail", pk=pk)


@dashboard_required
@role_required(*_manager_roles())
def programme_calendar(request, pk):
    org = _org_or_403(request)
    programme = get_object_or_404(Programme, pk=pk, organisation=org)
    year = int(request.GET.get("year", programme.start_date.year))
    month = int(request.GET.get("month", programme.start_date.month))
    cal = calendar.Calendar(firstweekday=0)
    weeks = []
    for week in cal.monthdatescalendar(year, month):
        row = []
        for day in week:
            in_range = programme.start_date <= day <= programme.end_date
            blocks = resolve_programme(programme, day) if in_range else None
            singles = list(
                ScheduleEvent.objects.filter(
                    programme=programme, kind=ScheduleEvent.Kind.SINGLE, date=day
                )
            )
            row.append(
                {
                    "date": day,
                    "in_month": day.month == month,
                    "in_range": in_range,
                    "week_label": week_label_for_date(programme, day)
                    if in_range and blocks is not None
                    else "",
                    "closed": in_range and blocks is None,
                    "has_override": bool(singles),
                }
            )
        weeks.append(row)
    return render(
        request,
        "dashboard/programme/programme_calendar.html",
        _prog_ctx(
            request,
            org,
            f"{programme.name} calendar",
            programme=programme,
            weeks=weeks,
            year=year,
            month=month,
            month_name=calendar.month_name[month],
        ),
    )


@dashboard_required
@role_required(*_manager_roles())
def programme_day(request, pk, date_str):
    org = _org_or_403(request)
    programme = get_object_or_404(Programme, pk=pk, organisation=org)
    target = date.fromisoformat(date_str)
    form = DayOverrideForm(request.POST or None)
    form.fields["activity"].queryset = Activity.objects.filter(organisation=org, is_active=True)
    if request.method == "POST" and form.is_valid():
        action = form.cleaned_data["action"]
        if action == "default":
            ScheduleEvent.objects.filter(
                programme=programme,
                kind=ScheduleEvent.Kind.SINGLE,
                date=target,
            ).delete()
            messages.success(request, "Day reset to default week pattern.")
        else:
            ScheduleEvent.objects.filter(
                programme=programme,
                kind=ScheduleEvent.Kind.SINGLE,
                date=target,
            ).delete()
            ScheduleEvent.objects.create(
                programme=programme,
                organisation=org,
                kind=ScheduleEvent.Kind.SINGLE,
                site=programme.site,
                session_type=programme.session_type,
                date=target,
                start_time=form.cleaned_data.get("start_time"),
                end_time=form.cleaned_data.get("end_time"),
                activity=form.cleaned_data.get("activity"),
                label=form.cleaned_data.get("label", ""),
                notes=form.cleaned_data.get("notes", ""),
                replaces_day=action == "replace" or form.cleaned_data.get("replaces_day", False),
            )
            messages.success(request, "Day override saved.")
        return redirect("dashboard:programme_calendar", pk=programme.pk)
    blocks = resolve_programme(programme, target)
    return render(
        request,
        "dashboard/programme/programme_day.html",
        _prog_ctx(
            request,
            org,
            f"{target.strftime('%A %d %B')}",
            programme=programme,
            target=target,
            blocks=blocks,
            week_label=week_label_for_date(programme, target),
            form=form,
        ),
    )


# --- Closures ---


@dashboard_required
@role_required(*_manager_roles())
def closure_list(request):
    org = _org_or_403(request)
    closures = ScheduleEvent.objects.filter(
        organisation=org,
        kind=ScheduleEvent.Kind.CLOSURE,
    ).select_related("programme", "site", "session_type")
    form = ScheduleEventClosureForm(request.POST or None)
    form.fields["programme"].queryset = Programme.objects.filter(organisation=org)
    form.fields["site"].queryset = Site.objects.filter(organisation=org)
    form.fields["session_type"].queryset = SessionType.objects.filter(organisation=org)
    if request.method == "POST" and form.is_valid():
        closure = form.save(commit=False)
        closure.organisation = org
        closure.kind = ScheduleEvent.Kind.CLOSURE
        closure.save()
        messages.success(request, "Closure period added.")
        return redirect("dashboard:closure_list")
    return render(
        request,
        "dashboard/programme/closures.html",
        _prog_ctx(request, org, "Closures", closures=closures, form=form),
    )
