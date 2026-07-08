import json
from contextlib import suppress

from accounts.decorators import dashboard_required, role_required
from accounts.models import User
from billing.models import Payment
from billing.services import stripe_service
from bookings.models import Booking, Child, Session
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from franchises.models import Franchise
from ofsted.models import Incident
from operations.forms import (
    AuthorisedCollectorForm,
    BulkSessionForm,
    CheckoutCollectorForm,
    ChildcareVoucherForm,
    MedicationForm,
    PaymentPlanForm,
    RecurringBookingForm,
    RefundForm,
    SafeguardingCaseForm,
    StaffComplianceForm,
    StaffShiftForm,
    SubsidyCodeForm,
    VisitorForm,
    VoucherRedeemForm,
    WalkInBookingForm,
)
from operations.models import (
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
    WaitlistEntry,
)
from operations.services import (
    bulk_check_in,
    checkout_with_collector,
    close_register,
    create_safeguarding_case_from_incident,
    create_walk_in_booking,
    export_register_csv,
    generate_sessions_bulk,
    get_organisation_analytics,
    get_register_rows,
    mark_no_show,
    promote_waitlist,
    redeem_voucher,
    verify_collector_pin,
)
from organisations.models import Site

from dashboard.mixins import dashboard_context
from dashboard.views import _org_or_403


def _ops_ctx(request, org, title: str, **extra):
    return {**dashboard_context(request, org), "title": title, **extra}


def _staff_roles():
    return (
        User.Role.SUPER_ADMIN,
        User.Role.ORG_ADMIN,
        User.Role.SITE_MANAGER,
        User.Role.STAFF,
    )


# --- Session register ---


@dashboard_required
@role_required(*_staff_roles())
def session_register(request, pk):
    org = _org_or_403(request)
    session = get_object_or_404(Session, pk=pk, organisation=org)
    ratio = None
    with suppress(Exception):
        ratio = session.ratio_checks.order_by("-checked_at").first()
    return render(
        request,
        "dashboard/operations/register.html",
        {
            **_ops_ctx(request, org, "Session register"),
            "session": session,
            "rows": get_register_rows(session),
            "ratio": ratio,
            "is_closed": bool(session.register_closed_at),
        },
    )


@dashboard_required
@role_required(*_staff_roles())
def export_register(request, pk):
    org = _org_or_403(request)
    session = get_object_or_404(Session, pk=pk, organisation=org)
    response = HttpResponse(export_register_csv(session), content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="register-{session.pk}.csv"'
    return response


@dashboard_required
@role_required(*_staff_roles())
@require_POST
def close_register_view(request, pk):
    org = _org_or_403(request)
    session = get_object_or_404(Session, pk=pk, organisation=org)
    close_register(session, request.user, request.POST.get("notes", ""))
    messages.success(request, "Register closed and session marked complete.")
    return redirect("dashboard:session_register", pk=pk)


@dashboard_required
@role_required(*_staff_roles())
@require_POST
def bulk_check_in_view(request, pk):
    org = _org_or_403(request)
    session = get_object_or_404(Session, pk=pk, organisation=org)
    count = bulk_check_in(session, request.user)
    messages.success(request, f"Checked in {count} children.")
    return redirect("dashboard:session_register", pk=pk)


@dashboard_required
@role_required(*_staff_roles())
@require_POST
def mark_no_show_view(request, booking_pk):
    org = _org_or_403(request)
    booking = get_object_or_404(Booking, pk=booking_pk, session__organisation=org)
    mark_no_show(booking)
    promote_waitlist(booking.session)
    return redirect("dashboard:session_register", pk=booking.session_id)


@dashboard_required
@role_required(*_staff_roles())
def walk_in_booking(request, pk):
    org = _org_or_403(request)
    session = get_object_or_404(Session, pk=pk, organisation=org)
    form = WalkInBookingForm(request.POST or None)
    form.fields["child"].queryset = Child.objects.filter(organisation=org, is_active=True)
    if request.method == "POST" and form.is_valid():
        create_walk_in_booking(
            session,
            form.cleaned_data["child"],
            request.user,
            payment_method=form.cleaned_data["payment_method"],
        )
        messages.success(request, "Walk-in booking added.")
        return redirect("dashboard:session_register", pk=pk)
    return render(
        request,
        "dashboard/operations/walk_in.html",
        {**_ops_ctx(request, org, "Walk-in booking"), "session": session, "form": form},
    )


@dashboard_required
@role_required(*_staff_roles())
def checkout_collector(request, booking_pk):
    org = _org_or_403(request)
    booking = get_object_or_404(Booking, pk=booking_pk, session__organisation=org)
    form = CheckoutCollectorForm(request.POST or None)
    form.fields["collector"].queryset = booking.child.authorised_collectors.filter(is_active=True)
    if request.method == "POST" and form.is_valid():
        collector = form.cleaned_data["collector"]
        pin = form.cleaned_data["pin_code"]
        if collector and not verify_collector_pin(collector, pin):
            messages.error(request, "Invalid collection PIN.")
        else:
            checkout_with_collector(
                booking,
                request.user,
                collector,
                form.cleaned_data["verified_name"],
            )
            if booking.late_fee_amount:
                from notifications.services import notify_late_fee

                notify_late_fee(booking, booking.late_fee_amount)
            messages.success(request, "Child checked out.")
            return redirect("dashboard:session_register", pk=booking.session_id)
    return render(
        request,
        "dashboard/operations/checkout_collector.html",
        {**_ops_ctx(request, org, "Collection"), "booking": booking, "form": form},
    )


# --- Calendar ---


@dashboard_required
@role_required(*_staff_roles())
def booking_calendar(request):
    org = _org_or_403(request)
    start = request.GET.get("start")
    end = request.GET.get("end")
    sessions = Session.objects.filter(organisation=org).select_related("session_type", "site")
    if start:
        sessions = sessions.filter(date__gte=start)
    if end:
        sessions = sessions.filter(date__lte=end)
    events = [
        {
            "title": f"{s.session_type.name} ({s.booked_count}/{s.session_type.capacity})",
            "start": str(s.date),
            "url": f"/dashboard/sessions/{s.pk}/register/",
        }
        for s in sessions[:200]
    ]
    if request.GET.get("format") == "json":
        return HttpResponse(json.dumps(events), content_type="application/json")
    return render(
        request,
        "dashboard/operations/calendar.html",
        {**_ops_ctx(request, org, "Booking calendar"), "events_json": json.dumps(events)},
    )


# --- Recurring, bulk, waitlist ---


@dashboard_required
@role_required(User.Role.SUPER_ADMIN, User.Role.ORG_ADMIN, User.Role.SITE_MANAGER)
def recurring_list(request):
    org = _org_or_403(request)
    patterns = RecurringBooking.objects.filter(child__organisation=org).select_related(
        "child", "session_type", "site"
    )
    return render(
        request,
        "dashboard/operations/recurring_list.html",
        {**_ops_ctx(request, org, "Recurring bookings"), "patterns": patterns},
    )


@dashboard_required
@role_required(User.Role.SUPER_ADMIN, User.Role.ORG_ADMIN, User.Role.SITE_MANAGER)
def recurring_create(request):
    org = _org_or_403(request)
    form = RecurringBookingForm(request.POST or None)
    form.fields["child"].queryset = Child.objects.filter(organisation=org, is_active=True)
    form.fields["session_type"].queryset = org.session_types.filter(is_active=True)
    form.fields["site"].queryset = Site.objects.filter(organisation=org)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Recurring booking pattern saved.")
        return redirect("dashboard:recurring_list")
    return render(
        request,
        "dashboard/operations/recurring_form.html",
        {**_ops_ctx(request, org, "Add recurring booking"), "form": form},
    )


@dashboard_required
@role_required(User.Role.SUPER_ADMIN, User.Role.ORG_ADMIN, User.Role.SITE_MANAGER)
def bulk_sessions(request):
    org = _org_or_403(request)
    form = BulkSessionForm(request.POST or None)
    form.fields["session_type"].queryset = org.session_types.filter(is_active=True)
    form.fields["site"].queryset = Site.objects.filter(organisation=org)
    created = None
    if request.method == "POST" and form.is_valid():
        created = generate_sessions_bulk(
            org,
            form.cleaned_data["session_type"],
            form.cleaned_data["site"],
            form.cleaned_data["start_date"],
            form.cleaned_data["end_date"],
            [int(d) for d in form.cleaned_data["weekdays"]],
            form.cleaned_data["start_time"],
            form.cleaned_data["end_time"],
        )
        messages.success(request, f"Created {created} sessions.")
        return redirect("dashboard:session_list")
    return render(
        request,
        "dashboard/operations/bulk_sessions.html",
        {**_ops_ctx(request, org, "Bulk session generator"), "form": form, "created": created},
    )


@dashboard_required
@role_required(*_staff_roles())
def waitlist_list(request):
    org = _org_or_403(request)
    entries = WaitlistEntry.objects.filter(session__organisation=org).select_related(
        "child", "session"
    )
    return render(
        request,
        "dashboard/operations/waitlist.html",
        {**_ops_ctx(request, org, "Waitlist"), "entries": entries},
    )


# --- Rota, visitors, medication, compliance ---


@dashboard_required
@role_required(User.Role.SUPER_ADMIN, User.Role.ORG_ADMIN, User.Role.SITE_MANAGER)
def rota_list(request):
    org = _org_or_403(request)
    shifts = StaffShift.objects.filter(site__organisation=org).select_related("user", "site")
    return render(
        request,
        "dashboard/operations/rota.html",
        {**_ops_ctx(request, org, "Staff rota"), "shifts": shifts},
    )


@dashboard_required
@role_required(User.Role.SUPER_ADMIN, User.Role.ORG_ADMIN, User.Role.SITE_MANAGER)
def rota_create(request):
    org = _org_or_403(request)
    form = StaffShiftForm(request.POST or None)
    form.fields["site"].queryset = Site.objects.filter(organisation=org)
    form.fields["user"].queryset = User.objects.filter(
        organisation=org, role__in=[User.Role.STAFF, User.Role.SITE_MANAGER]
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Shift added to rota.")
        return redirect("dashboard:rota_list")
    return render(
        request,
        "dashboard/operations/rota_form.html",
        {**_ops_ctx(request, org, "Add shift"), "form": form},
    )


@dashboard_required
@role_required(*_staff_roles())
def visitor_list(request):
    org = _org_or_403(request)
    visitors = Visitor.objects.filter(site__organisation=org).select_related("site")
    form = VisitorForm(request.POST or None)
    form.fields["site"].queryset = Site.objects.filter(organisation=org)
    if request.method == "POST" and form.is_valid():
        visitor = form.save(commit=False)
        visitor.signed_in_at = timezone.now()
        visitor.signed_in_by = request.user
        visitor.save()
        messages.success(request, "Visitor signed in.")
        return redirect("dashboard:visitor_list")
    return render(
        request,
        "dashboard/operations/visitors.html",
        {**_ops_ctx(request, org, "Visitors"), "visitors": visitors, "form": form},
    )


@dashboard_required
@role_required(*_staff_roles())
@require_POST
def visitor_sign_out(request, pk):
    org = _org_or_403(request)
    visitor = get_object_or_404(Visitor, pk=pk, site__organisation=org)
    visitor.signed_out_at = timezone.now()
    visitor.save(update_fields=["signed_out_at"])
    return redirect("dashboard:visitor_list")


@dashboard_required
@role_required(*_staff_roles())
def medication_list(request):
    org = _org_or_403(request)
    logs = MedicationAdministration.objects.filter(child__organisation=org).select_related(
        "child", "session"
    )[:100]
    form = MedicationForm(request.POST or None)
    form.fields["child"].queryset = Child.objects.filter(organisation=org, is_active=True)
    form.fields["session"].queryset = Session.objects.filter(organisation=org)
    if request.method == "POST" and form.is_valid():
        entry = form.save(commit=False)
        entry.administered_by = request.user
        entry.save()
        messages.success(request, "Medication log recorded.")
        return redirect("dashboard:medication_list")
    return render(
        request,
        "dashboard/operations/medication.html",
        {**_ops_ctx(request, org, "Medication log"), "logs": logs, "form": form},
    )


@dashboard_required
@role_required(User.Role.SUPER_ADMIN, User.Role.ORG_ADMIN)
def staff_compliance_list(request):
    org = _org_or_403(request)
    staff = User.objects.filter(organisation=org, role__in=_staff_roles())
    return render(
        request,
        "dashboard/operations/compliance.html",
        {**_ops_ctx(request, org, "Staff compliance"), "staff": staff},
    )


@dashboard_required
@role_required(User.Role.SUPER_ADMIN, User.Role.ORG_ADMIN)
def staff_compliance_edit(request, user_pk):
    org = _org_or_403(request)
    staff_user = get_object_or_404(User, pk=user_pk, organisation=org)
    compliance, _ = StaffCompliance.objects.get_or_create(user=staff_user)
    form = StaffComplianceForm(request.POST or None, instance=compliance)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Compliance record updated.")
        return redirect("dashboard:staff_compliance_list")
    return render(
        request,
        "dashboard/operations/compliance_form.html",
        {
            **_ops_ctx(request, org, "Staff compliance"),
            "form": form,
            "staff_user": staff_user,
        },
    )


# --- Safeguarding, finance ---


@dashboard_required
@role_required(User.Role.SUPER_ADMIN, User.Role.ORG_ADMIN, User.Role.SITE_MANAGER)
def safeguarding_list(request):
    org = _org_or_403(request)
    cases = SafeguardingCase.objects.filter(organisation=org).select_related("child", "assigned_to")
    return render(
        request,
        "dashboard/operations/safeguarding.html",
        {**_ops_ctx(request, org, "Safeguarding"), "cases": cases},
    )


@dashboard_required
@role_required(User.Role.SUPER_ADMIN, User.Role.ORG_ADMIN, User.Role.SITE_MANAGER)
def safeguarding_create(request, incident_pk=None):
    org = _org_or_403(request)
    incident = None
    if incident_pk:
        incident = get_object_or_404(Incident, pk=incident_pk, organisation=org)
        if request.method == "GET":
            case = create_safeguarding_case_from_incident(incident, request.user)
            from notifications.services import notify_safeguarding_escalation

            notify_safeguarding_escalation(case)
            messages.success(request, "Safeguarding case opened from incident.")
            return redirect("dashboard:safeguarding_list")
    form = SafeguardingCaseForm(request.POST or None)
    form.fields["child"].queryset = Child.objects.filter(organisation=org)
    form.fields["assigned_to"].queryset = User.objects.filter(
        organisation=org,
        role__in=[User.Role.STAFF, User.Role.SITE_MANAGER, User.Role.ORG_ADMIN],
    )
    if request.method == "POST" and form.is_valid():
        case = form.save(commit=False)
        case.organisation = org
        if incident:
            case.incident = incident
        case.save()
        from notifications.services import notify_safeguarding_escalation

        notify_safeguarding_escalation(case)
        messages.success(request, "Safeguarding case created.")
        return redirect("dashboard:safeguarding_list")
    return render(
        request,
        "dashboard/operations/safeguarding_form.html",
        {**_ops_ctx(request, org, "New safeguarding case"), "form": form, "incident": incident},
    )


@dashboard_required
@role_required(User.Role.SUPER_ADMIN, User.Role.ORG_ADMIN, User.Role.FINANCE)
def subsidy_list(request):
    org = _org_or_403(request)
    codes = SubsidyCode.objects.filter(organisation=org)
    form = SubsidyCodeForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        code = form.save(commit=False)
        code.organisation = org
        code.save()
        messages.success(request, "Subsidy code saved.")
        return redirect("dashboard:subsidy_list")
    return render(
        request,
        "dashboard/operations/subsidies.html",
        {**_ops_ctx(request, org, "Subsidy codes"), "codes": codes, "form": form},
    )


@dashboard_required
@role_required(User.Role.SUPER_ADMIN, User.Role.ORG_ADMIN, User.Role.FINANCE)
def voucher_list(request):
    org = _org_or_403(request)
    vouchers = ChildcareVoucher.objects.filter(organisation=org).select_related("parent", "child")
    form = ChildcareVoucherForm(request.POST or None)
    form.fields["parent"].queryset = User.objects.filter(organisation=org, role=User.Role.PARENT)
    form.fields["child"].queryset = Child.objects.filter(organisation=org)
    if request.method == "POST" and form.is_valid():
        voucher = form.save(commit=False)
        voucher.organisation = org
        voucher.save()
        messages.success(request, "Voucher account added.")
        return redirect("dashboard:voucher_list")
    return render(
        request,
        "dashboard/operations/vouchers.html",
        {**_ops_ctx(request, org, "Childcare vouchers"), "vouchers": vouchers, "form": form},
    )


@dashboard_required
@role_required(User.Role.SUPER_ADMIN, User.Role.ORG_ADMIN, User.Role.FINANCE)
def voucher_redeem(request):
    org = _org_or_403(request)
    form = VoucherRedeemForm(request.POST or None)
    form.fields["voucher"].queryset = ChildcareVoucher.objects.filter(
        organisation=org, is_active=True
    )
    form.fields["booking"].queryset = Booking.objects.filter(
        session__organisation=org, payment_status=Booking.PaymentStatus.UNPAID
    )
    if request.method == "POST" and form.is_valid():
        redemption = redeem_voucher(form.cleaned_data["booking"], form.cleaned_data["voucher"])
        from notifications.services import notify_voucher_redemption

        notify_voucher_redemption(redemption.booking, redemption.voucher, redemption.amount)
        messages.success(request, f"Redeemed £{redemption.amount} from voucher.")
        return redirect("dashboard:voucher_list")
    return render(
        request,
        "dashboard/operations/voucher_redeem.html",
        {**_ops_ctx(request, org, "Redeem voucher"), "form": form},
    )


@dashboard_required
@role_required(User.Role.SUPER_ADMIN, User.Role.ORG_ADMIN, User.Role.FINANCE)
def payment_plan_list(request):
    org = _org_or_403(request)
    plans = PaymentPlan.objects.filter(organisation=org).select_related("child")
    form = PaymentPlanForm(request.POST or None)
    form.fields["child"].queryset = Child.objects.filter(organisation=org)
    if request.method == "POST" and form.is_valid():
        plan = form.save(commit=False)
        plan.organisation = org
        plan.save()
        messages.success(request, "Payment plan created.")
        return redirect("dashboard:payment_plan_list")
    return render(
        request,
        "dashboard/operations/payment_plans.html",
        {**_ops_ctx(request, org, "Payment plans"), "plans": plans, "form": form},
    )


@dashboard_required
@role_required(User.Role.SUPER_ADMIN, User.Role.ORG_ADMIN, User.Role.FINANCE)
def refund_payment_view(request, payment_pk):
    org = _org_or_403(request)
    payment = get_object_or_404(Payment, pk=payment_pk, organisation=org)
    form = RefundForm(request.POST or None, initial={"amount": payment.amount})
    if request.method == "POST" and form.is_valid():
        stripe_service.refund_payment(
            payment,
            form.cleaned_data.get("amount") or payment.amount,
            form.cleaned_data.get("reason", ""),
            request.user,
        )
        messages.success(request, "Refund processed.")
        return redirect("dashboard:finance")
    return render(
        request,
        "dashboard/operations/refund.html",
        {**_ops_ctx(request, org, "Refund payment"), "payment": payment, "form": form},
    )


@dashboard_required
@role_required(*_staff_roles())
def analytics_dashboard(request):
    org = _org_or_403(request)
    stats = get_organisation_analytics(org) if org else {}
    return render(
        request,
        "dashboard/operations/analytics.html",
        {**_ops_ctx(request, org, "Analytics"), "stats": stats},
    )


@dashboard_required
@role_required(User.Role.SUPER_ADMIN, User.Role.ORG_ADMIN)
def collector_list(request, child_pk):
    org = _org_or_403(request)
    child = get_object_or_404(Child, pk=child_pk, organisation=org)
    form = AuthorisedCollectorForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        collector = form.save(commit=False)
        collector.child = child
        collector.save()
        messages.success(request, "Authorised collector added.")
        return redirect("dashboard:collector_list", child_pk=child.pk)
    return render(
        request,
        "dashboard/operations/collectors.html",
        {
            **_ops_ctx(request, org, "Authorised collectors"),
            "child": child,
            "collectors": child.authorised_collectors.all(),
            "form": form,
        },
    )


@dashboard_required
@role_required(User.Role.SUPER_ADMIN)
def franchise_onboarding(request, franchise_pk):
    franchise = get_object_or_404(Franchise, pk=franchise_pk)
    tasks = [
        ("stripe", "Configure Stripe"),
        ("xero", "Connect Xero"),
        ("domain", "Set up custom domain"),
        ("first_org", "Create first organisation"),
        ("first_session", "Schedule first session"),
        ("staff", "Invite staff users"),
    ]
    for key, label in tasks:
        FranchiseOnboardingTask.objects.get_or_create(
            franchise=franchise, task_key=key, defaults={"label": label}
        )
    if request.method == "POST":
        task = get_object_or_404(
            FranchiseOnboardingTask, pk=request.POST.get("task_id"), franchise=franchise
        )
        task.completed_at = timezone.now()
        task.save(update_fields=["completed_at"])
        return redirect("dashboard:franchise_onboarding", franchise_pk=franchise.pk)
    onboarding = franchise.onboarding_tasks.all()
    return render(
        request,
        "dashboard/operations/franchise_onboarding.html",
        {
            **_ops_ctx(request, None, "Franchise onboarding"),
            "franchise": franchise,
            "onboarding": onboarding,
        },
    )
