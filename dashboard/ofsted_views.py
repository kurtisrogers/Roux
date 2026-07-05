from datetime import date

from accounts.decorators import dashboard_required, role_required
from accounts.models import User
from bookings.models import Booking, Session
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from ofsted.forms import IncidentForm
from ofsted.models import Incident, OfstedReport, RatioCheck
from ofsted.ratios import analyse_session_ratio
from ofsted.services import (
    check_session_ratio,
    export_incidents_csv,
    export_ratio_checks_csv,
    generate_monthly_report,
)

from dashboard.mixins import dashboard_context, resolve_organisation


def _org_or_403(request):
    org = resolve_organisation(request)
    if not org and request.user.role != User.Role.SUPER_ADMIN:
        messages.error(request, "No organisation assigned to your account.")
        return None
    if org and not request.user.has_org_access(org):
        from django.core.exceptions import PermissionDenied

        raise PermissionDenied
    return org


@dashboard_required
@role_required(User.Role.SUPER_ADMIN, User.Role.ORG_ADMIN, User.Role.SITE_MANAGER)
def ofsted_dashboard(request):
    org = _org_or_403(request)
    today = timezone.now().date()
    month_start = today.replace(day=1)

    incidents = Incident.objects.filter(organisation=org)[:10] if org else []
    recent_checks = (
        RatioCheck.objects.filter(session__organisation=org).select_related("session")[:10]
        if org
        else []
    )
    reports = OfstedReport.objects.filter(organisation=org)[:5] if org else []

    non_compliant = (
        RatioCheck.objects.filter(session__organisation=org, compliant=False).count() if org else 0
    )

    return render(
        request,
        "dashboard/ofsted/index.html",
        {
            **dashboard_context(request, org),
            "incidents": incidents,
            "recent_checks": recent_checks,
            "reports": reports,
            "non_compliant_count": non_compliant,
            "month_start": month_start,
            "today": today,
        },
    )


@dashboard_required
@role_required(User.Role.SUPER_ADMIN, User.Role.ORG_ADMIN, User.Role.SITE_MANAGER, User.Role.STAFF)
def incident_list(request):
    org = _org_or_403(request)
    incidents = Incident.objects.filter(organisation=org).select_related("child", "session")
    return render(
        request,
        "dashboard/ofsted/incidents.html",
        {**dashboard_context(request, org), "incidents": incidents},
    )


@dashboard_required
@role_required(User.Role.SUPER_ADMIN, User.Role.ORG_ADMIN, User.Role.SITE_MANAGER, User.Role.STAFF)
def incident_create(request):
    org = _org_or_403(request)
    if request.method == "POST":
        form = IncidentForm(request.POST)
        if form.is_valid():
            incident = form.save(commit=False)
            incident.organisation = org
            incident.reported_by = request.user
            incident.save()
            messages.success(request, "Incident recorded.")
            return redirect("dashboard:incident_list")
    else:
        form = IncidentForm()
        form.fields["session"].queryset = Session.objects.filter(organisation=org)
        from bookings.models import Child

        form.fields["child"].queryset = Child.objects.filter(organisation=org)
    return render(
        request,
        "dashboard/ofsted/incident_form.html",
        {**dashboard_context(request, org), "form": form, "title": "Record Incident"},
    )


@dashboard_required
@role_required(User.Role.SUPER_ADMIN, User.Role.ORG_ADMIN, User.Role.SITE_MANAGER, User.Role.STAFF)
def ratio_check_session(request, session_pk):
    org = _org_or_403(request)
    session = get_object_or_404(Session, pk=session_pk, organisation=org)
    check = check_session_ratio(session, checked_by=request.user)
    if check.compliant:
        messages.success(
            request, f"Ratio compliant: {check.staff_count} staff for {check.child_count} children."
        )
    else:
        messages.warning(
            request,
            f"Ratio NON-COMPLIANT: need {check.required_staff} staff, have {check.staff_count}.",
        )
    return redirect("dashboard:session_detail", pk=session_pk)


@dashboard_required
@role_required(User.Role.SUPER_ADMIN, User.Role.ORG_ADMIN, User.Role.SITE_MANAGER)
def ratio_overview(request):
    org = _org_or_403(request)
    today = timezone.now().date()
    sessions = (
        Session.objects.filter(
            organisation=org,
            date=today,
            status__in=[Session.Status.SCHEDULED, Session.Status.IN_PROGRESS],
        )
        .select_related("session_type", "site")
        .prefetch_related("staff", "bookings__child")
    )

    session_ratios = []
    for session in sessions:
        ages = [
            b.child.age
            for b in session.bookings.filter(
                status__in=[Booking.Status.CONFIRMED, Booking.Status.CHECKED_IN]
            )
        ]
        analysis = analyse_session_ratio(ages, session.staff.count())
        session_ratios.append({"session": session, "analysis": analysis})

    return render(
        request,
        "dashboard/ofsted/ratios.html",
        {**dashboard_context(request, org), "session_ratios": session_ratios, "today": today},
    )


@dashboard_required
@role_required(User.Role.SUPER_ADMIN, User.Role.ORG_ADMIN, User.Role.SITE_MANAGER)
@require_POST
def generate_report(request):
    org = _org_or_403(request)
    period_start = date.fromisoformat(request.POST.get("period_start"))
    period_end = date.fromisoformat(request.POST.get("period_end"))
    report = generate_monthly_report(org, period_start, period_end, user=request.user)
    messages.success(
        request, f"Report generated: {report.data['compliance_rate']}% ratio compliance."
    )
    return redirect("dashboard:ofsted_dashboard")


@dashboard_required
@role_required(User.Role.SUPER_ADMIN, User.Role.ORG_ADMIN, User.Role.SITE_MANAGER)
def export_incidents(request):
    org = _org_or_403(request)
    period_start = date.fromisoformat(
        request.GET.get("start", str(timezone.now().date().replace(day=1)))
    )
    period_end = date.fromisoformat(request.GET.get("end", str(timezone.now().date())))
    csv_content = export_incidents_csv(org, period_start, period_end)
    response = HttpResponse(csv_content, content_type="text/csv")
    response["Content-Disposition"] = (
        f'attachment; filename="incidents_{period_start}_{period_end}.csv"'
    )
    return response


@dashboard_required
@role_required(User.Role.SUPER_ADMIN, User.Role.ORG_ADMIN, User.Role.SITE_MANAGER)
def export_ratios(request):
    org = _org_or_403(request)
    period_start = date.fromisoformat(
        request.GET.get("start", str(timezone.now().date().replace(day=1)))
    )
    period_end = date.fromisoformat(request.GET.get("end", str(timezone.now().date())))
    csv_content = export_ratio_checks_csv(org, period_start, period_end)
    response = HttpResponse(csv_content, content_type="text/csv")
    response["Content-Disposition"] = (
        f'attachment; filename="ratio_checks_{period_start}_{period_end}.csv"'
    )
    return response
