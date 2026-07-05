import csv
import io
from datetime import date

from bookings.models import Booking, Session

from ofsted.models import Incident, OfstedReport, RatioCheck
from ofsted.ratios import analyse_session_ratio


def check_session_ratio(session, checked_by=None) -> RatioCheck:
    bookings = session.bookings.filter(
        status__in=[Booking.Status.CONFIRMED, Booking.Status.CHECKED_IN]
    ).select_related("child")
    ages = [b.child.age for b in bookings]
    staff_count = session.staff.count()
    analysis = analyse_session_ratio(ages, staff_count)

    return RatioCheck.objects.create(
        session=session,
        checked_by=checked_by,
        child_count=analysis["child_count"],
        staff_count=analysis["staff_count"],
        required_staff=analysis["required_staff"],
        compliant=analysis["compliant"],
        age_groups=analysis["age_groups"],
    )


def generate_monthly_report(
    organisation, period_start: date, period_end: date, user=None
) -> OfstedReport:
    sessions = Session.objects.filter(
        organisation=organisation,
        date__range=(period_start, period_end),
    )
    incidents = Incident.objects.filter(
        organisation=organisation,
        occurred_at__date__range=(period_start, period_end),
    )
    ratio_checks = RatioCheck.objects.filter(
        session__organisation=organisation,
        checked_at__date__range=(period_start, period_end),
    )

    non_compliant = ratio_checks.filter(compliant=False).count()
    ofsted_notifiable = incidents.filter(ofsted_notifiable=True).count()

    data = {
        "period_start": str(period_start),
        "period_end": str(period_end),
        "total_sessions": sessions.count(),
        "total_bookings": Booking.objects.filter(
            session__organisation=organisation,
            session__date__range=(period_start, period_end),
        ).count(),
        "total_incidents": incidents.count(),
        "incidents_by_type": {
            t: incidents.filter(incident_type=t).count() for t, _ in Incident.Type.choices
        },
        "ofsted_notifiable_incidents": ofsted_notifiable,
        "ratio_checks": ratio_checks.count(),
        "non_compliant_ratio_checks": non_compliant,
        "compliance_rate": (
            round((ratio_checks.count() - non_compliant) / ratio_checks.count() * 100, 1)
            if ratio_checks.count()
            else 100.0
        ),
    }

    return OfstedReport.objects.create(
        organisation=organisation,
        report_type=OfstedReport.ReportType.MONTHLY,
        period_start=period_start,
        period_end=period_end,
        generated_by=user,
        data=data,
    )


def export_incidents_csv(organisation, period_start: date, period_end: date) -> str:
    incidents = Incident.objects.filter(
        organisation=organisation,
        occurred_at__date__range=(period_start, period_end),
    ).select_related("child", "session", "reported_by")

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "Date",
            "Type",
            "Severity",
            "Child",
            "Location",
            "Description",
            "Action Taken",
            "Parent Notified",
            "Ofsted Notifiable",
            "Reported By",
        ]
    )
    for inc in incidents:
        writer.writerow(
            [
                inc.occurred_at.strftime("%Y-%m-%d %H:%M"),
                inc.get_incident_type_display(),
                inc.get_severity_display(),
                inc.child.full_name if inc.child else "",
                inc.location,
                inc.description,
                inc.action_taken,
                "Yes" if inc.parent_notified else "No",
                "Yes" if inc.ofsted_notifiable else "No",
                inc.reported_by.get_full_name() if inc.reported_by else "",
            ]
        )
    return output.getvalue()


def export_ratio_checks_csv(organisation, period_start: date, period_end: date) -> str:
    checks = RatioCheck.objects.filter(
        session__organisation=organisation,
        checked_at__date__range=(period_start, period_end),
    ).select_related("session", "session__site", "checked_by")

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "Date",
            "Session",
            "Site",
            "Children",
            "Staff",
            "Required Staff",
            "Compliant",
            "Age Groups",
            "Checked By",
        ]
    )
    for check in checks:
        writer.writerow(
            [
                check.checked_at.strftime("%Y-%m-%d %H:%M"),
                str(check.session),
                check.session.site.name,
                check.child_count,
                check.staff_count,
                check.required_staff,
                "Yes" if check.compliant else "NO",
                str(check.age_groups),
                check.checked_by.get_full_name() if check.checked_by else "",
            ]
        )
    return output.getvalue()
