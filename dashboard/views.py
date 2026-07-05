import json
from datetime import timedelta

from accounts.decorators import dashboard_required, role_required
from accounts.forms import UserForm
from accounts.models import User
from billing.models import Payment
from billing.services import stripe_service
from bookings.models import Attendance, Booking, Child, Session, SessionType
from cms.block_forms import get_content_form
from cms.models import ContactSubmission, Page, PageBlock, SiteSettings
from django.contrib import messages
from django.db.models import Count
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from finance.models import XeroConnection, XeroInvoice
from finance.services import xero_service
from organisations.models import Organisation, Site

from dashboard.forms import (
    ChildForm,
    PageBlockForm,
    PageForm,
    SessionForm,
    SessionTypeForm,
    SiteForm,
    SiteSettingsForm,
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
def home(request):
    org = _org_or_403(request)
    ctx = dashboard_context(request, org)
    today = timezone.now().date()
    week_end = today + timedelta(days=7)

    if org:
        ctx.update(
            {
                "today_sessions": Session.objects.filter(organisation=org, date=today).count(),
                "week_bookings": Booking.objects.filter(
                    session__organisation=org,
                    session__date__range=(today, week_end),
                    status__in=[Booking.Status.CONFIRMED, Booking.Status.CHECKED_IN],
                ).count(),
                "total_children": Child.objects.filter(organisation=org, is_active=True).count(),
                "unpaid_bookings": Booking.objects.filter(
                    session__organisation=org,
                    payment_status=Booking.PaymentStatus.UNPAID,
                    status=Booking.Status.CONFIRMED,
                ).count(),
                "recent_bookings": Booking.objects.filter(session__organisation=org).select_related(
                    "child", "session"
                )[:8],
                "upcoming_sessions": Session.objects.filter(
                    organisation=org,
                    date__gte=today,
                    status=Session.Status.SCHEDULED,
                ).select_related("session_type", "site")[:6],
                "unread_contacts": ContactSubmission.objects.filter(
                    organisation=org, is_read=False
                ).count(),
            }
        )
    elif request.user.role == User.Role.SUPER_ADMIN:
        ctx["organisations"] = Organisation.objects.annotate(
            user_count=Count("users"),
            child_count=Count("children"),
        )

    return render(request, "dashboard/home.html", ctx)


# --- Children ---


@dashboard_required
@role_required(User.Role.SUPER_ADMIN, User.Role.ORG_ADMIN, User.Role.SITE_MANAGER, User.Role.STAFF)
def child_list(request):
    org = _org_or_403(request)
    children = Child.objects.filter(organisation=org) if org else Child.objects.all()
    if request.user.role == User.Role.PARENT:
        children = children.filter(parent=request.user)
    return render(
        request,
        "dashboard/children/list.html",
        {**dashboard_context(request, org), "children": children},
    )


@dashboard_required
def child_create(request):
    org = _org_or_403(request)
    if request.method == "POST":
        form = ChildForm(request.POST)
        if form.is_valid():
            child = form.save(commit=False)
            child.organisation = org
            child.parent = request.user
            child.save()
            messages.success(request, f"Added {child.full_name}.")
            return redirect("dashboard:child_list")
    else:
        form = ChildForm()
    return render(
        request,
        "dashboard/children/form.html",
        {**dashboard_context(request, org), "form": form, "title": "Add Child"},
    )


@dashboard_required
def child_edit(request, pk):
    org = _org_or_403(request)
    child = get_object_or_404(Child, pk=pk, organisation=org)
    if request.method == "POST":
        form = ChildForm(request.POST, instance=child)
        if form.is_valid():
            form.save()
            messages.success(request, "Child updated.")
            return redirect("dashboard:child_list")
    else:
        form = ChildForm(instance=child)
    return render(
        request,
        "dashboard/children/form.html",
        {**dashboard_context(request, org), "form": form, "title": "Edit Child", "child": child},
    )


# --- Sessions ---


@dashboard_required
@role_required(User.Role.SUPER_ADMIN, User.Role.ORG_ADMIN, User.Role.SITE_MANAGER, User.Role.STAFF)
def session_list(request):
    org = _org_or_403(request)
    sessions = (
        Session.objects.filter(organisation=org) if org else Session.objects.all()
    ).select_related("session_type", "site")
    return render(
        request,
        "dashboard/sessions/list.html",
        {**dashboard_context(request, org), "sessions": sessions},
    )


@dashboard_required
@role_required(User.Role.SUPER_ADMIN, User.Role.ORG_ADMIN, User.Role.SITE_MANAGER)
def session_create(request):
    org = _org_or_403(request)
    if request.method == "POST":
        form = SessionForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.organisation = org
            session.save()
            form.save_m2m()
            messages.success(request, "Session created.")
            return redirect("dashboard:session_list")
    else:
        form = SessionForm()
        form.fields["site"].queryset = Site.objects.filter(organisation=org)
        form.fields["session_type"].queryset = SessionType.objects.filter(organisation=org)
        form.fields["staff"].queryset = User.objects.filter(
            organisation=org, role__in=[User.Role.STAFF, User.Role.SITE_MANAGER]
        )
    return render(
        request,
        "dashboard/sessions/form.html",
        {**dashboard_context(request, org), "form": form, "title": "Add Session"},
    )


@dashboard_required
@role_required(User.Role.SUPER_ADMIN, User.Role.ORG_ADMIN, User.Role.SITE_MANAGER, User.Role.STAFF)
def session_detail(request, pk):
    org = _org_or_403(request)
    session = get_object_or_404(Session, pk=pk, organisation=org)
    bookings = session.bookings.select_related("child", "child__parent")
    return render(
        request,
        "dashboard/sessions/detail.html",
        {**dashboard_context(request, org), "session": session, "bookings": bookings},
    )


@dashboard_required
@role_required(User.Role.SUPER_ADMIN, User.Role.ORG_ADMIN, User.Role.SITE_MANAGER, User.Role.STAFF)
@require_POST
def check_in(request, booking_pk):
    org = _org_or_403(request)
    booking = get_object_or_404(Booking, pk=booking_pk, session__organisation=org)
    attendance, _ = Attendance.objects.get_or_create(booking=booking)
    attendance.checked_in_at = timezone.now()
    attendance.checked_in_by = request.user
    attendance.save()
    booking.status = Booking.Status.CHECKED_IN
    booking.save(update_fields=["status"])
    if request.htmx:
        return render(request, "dashboard/partials/booking_row.html", {"booking": booking})
    return redirect("dashboard:session_detail", pk=booking.session_id)


@dashboard_required
@role_required(User.Role.SUPER_ADMIN, User.Role.ORG_ADMIN, User.Role.SITE_MANAGER, User.Role.STAFF)
@require_POST
def check_out(request, booking_pk):
    org = _org_or_403(request)
    booking = get_object_or_404(Booking, pk=booking_pk, session__organisation=org)
    attendance, _ = Attendance.objects.get_or_create(booking=booking)
    attendance.checked_out_at = timezone.now()
    attendance.checked_out_by = request.user
    attendance.save()
    booking.status = Booking.Status.CHECKED_OUT
    booking.save(update_fields=["status"])
    if request.htmx:
        return render(request, "dashboard/partials/booking_row.html", {"booking": booking})
    return redirect("dashboard:session_detail", pk=booking.session_id)


# --- Session Types ---


@dashboard_required
@role_required(User.Role.SUPER_ADMIN, User.Role.ORG_ADMIN)
def session_type_list(request):
    org = _org_or_403(request)
    types = SessionType.objects.filter(organisation=org)
    return render(
        request,
        "dashboard/session_types/list.html",
        {**dashboard_context(request, org), "session_types": types},
    )


@dashboard_required
@role_required(User.Role.SUPER_ADMIN, User.Role.ORG_ADMIN)
def session_type_create(request):
    org = _org_or_403(request)
    if request.method == "POST":
        form = SessionTypeForm(request.POST)
        if form.is_valid():
            st = form.save(commit=False)
            st.organisation = org
            st.save()
            messages.success(request, "Session type created.")
            return redirect("dashboard:session_type_list")
    else:
        form = SessionTypeForm()
    return render(
        request,
        "dashboard/session_types/form.html",
        {**dashboard_context(request, org), "form": form, "title": "Add Session Type"},
    )


# --- Bookings ---


@dashboard_required
def booking_list(request):
    org = _org_or_403(request)
    bookings = Booking.objects.filter(session__organisation=org) if org else Booking.objects.all()
    if request.user.role == User.Role.PARENT:
        bookings = bookings.filter(booked_by=request.user)
    bookings = bookings.select_related("child", "session", "session__session_type")
    return render(
        request,
        "dashboard/bookings/list.html",
        {**dashboard_context(request, org), "bookings": bookings},
    )


# --- CMS ---


@dashboard_required
@role_required(User.Role.SUPER_ADMIN, User.Role.ORG_ADMIN, User.Role.SITE_MANAGER)
def page_list(request):
    org = _org_or_403(request)
    pages = Page.objects.filter(organisation=org)
    return render(
        request,
        "dashboard/cms/pages/list.html",
        {**dashboard_context(request, org), "pages": pages},
    )


@dashboard_required
@role_required(User.Role.SUPER_ADMIN, User.Role.ORG_ADMIN, User.Role.SITE_MANAGER)
def page_create(request):
    org = _org_or_403(request)
    if request.method == "POST":
        form = PageForm(request.POST)
        if form.is_valid():
            page = form.save(commit=False)
            page.organisation = org
            page.save()
            messages.success(request, "Page created.")
            return redirect("dashboard:page_edit", pk=page.pk)
    else:
        form = PageForm()
    return render(
        request,
        "dashboard/cms/pages/form.html",
        {**dashboard_context(request, org), "form": form, "title": "New Page"},
    )


@dashboard_required
@role_required(User.Role.SUPER_ADMIN, User.Role.ORG_ADMIN, User.Role.SITE_MANAGER)
def page_edit(request, pk):
    org = _org_or_403(request)
    page = get_object_or_404(Page, pk=pk, organisation=org)
    if request.method == "POST":
        form = PageForm(request.POST, instance=page)
        if form.is_valid():
            form.save()
            messages.success(request, "Page saved.")
            return redirect("dashboard:page_edit", pk=page.pk)
    else:
        form = PageForm(instance=page)
    blocks = page.blocks.all()
    return render(
        request,
        "dashboard/cms/pages/edit.html",
        {
            **dashboard_context(request, org),
            "form": form,
            "page": page,
            "blocks": blocks,
            "block_types": PageBlock.BlockType.choices,
        },
    )


@dashboard_required
@role_required(User.Role.SUPER_ADMIN, User.Role.ORG_ADMIN, User.Role.SITE_MANAGER)
@require_POST
def block_add(request, page_pk):
    org = _org_or_403(request)
    page = get_object_or_404(Page, pk=page_pk, organisation=org)
    block_type = request.POST.get("block_type", PageBlock.BlockType.RICH_TEXT)
    defaults = _default_block_content(block_type)
    order = page.blocks.count()
    PageBlock.objects.create(
        page=page,
        block_type=block_type,
        order=order,
        content=defaults,
    )
    if request.htmx:
        blocks = page.blocks.all()
        return render(
            request,
            "dashboard/cms/pages/partials/block_list.html",
            {"blocks": blocks, "page": page, "block_types": PageBlock.BlockType.choices},
        )
    return redirect("dashboard:page_edit", pk=page.pk)


@dashboard_required
@role_required(User.Role.SUPER_ADMIN, User.Role.ORG_ADMIN, User.Role.SITE_MANAGER)
def block_edit(request, pk):
    org = _org_or_403(request)
    block = get_object_or_404(PageBlock, pk=pk, page__organisation=org)
    content_form = get_content_form(block.block_type, content=block.content)
    meta_form = PageBlockForm(instance=block)

    if request.method == "POST":
        meta_form = PageBlockForm(request.POST, instance=block)
        content_form = (
            get_content_form(block.block_type, data=request.POST) if content_form else None
        )

        meta_valid = meta_form.is_valid()
        content_valid = content_form.is_valid() if content_form else True

        if meta_valid and content_valid:
            block.block_type = meta_form.cleaned_data["block_type"]
            block.is_visible = meta_form.cleaned_data["is_visible"]
            if content_form:
                block.content = content_form.to_content()
            else:
                try:
                    block.content = json.loads(request.POST.get("content", "{}"))
                except json.JSONDecodeError:
                    messages.error(request, "Invalid JSON in block content.")
                    if request.htmx:
                        return render(
                            request,
                            "dashboard/cms/pages/partials/block_edit_form.html",
                            {
                                "meta_form": meta_form,
                                "content_form": content_form,
                                "block": block,
                                "page": block.page,
                                "raw_content": json.dumps(block.content, indent=2),
                            },
                        )
                    return redirect("dashboard:page_edit", pk=block.page_id)
            block.save()
            messages.success(request, "Block updated.")
            if request.htmx:
                return render(
                    request,
                    "dashboard/cms/pages/partials/block_item.html",
                    {"block": block, "page": block.page},
                )
            return redirect("dashboard:page_edit", pk=block.page_id)

    return render(
        request,
        "dashboard/cms/pages/partials/block_edit_form.html",
        {
            "meta_form": meta_form,
            "content_form": content_form,
            "block": block,
            "page": block.page,
            "raw_content": json.dumps(block.content, indent=2),
        },
    )


@dashboard_required
@role_required(User.Role.SUPER_ADMIN, User.Role.ORG_ADMIN, User.Role.SITE_MANAGER)
@require_POST
def block_delete(request, pk):
    org = _org_or_403(request)
    block = get_object_or_404(PageBlock, pk=pk, page__organisation=org)
    page = block.page
    block.delete()
    if request.htmx:
        return render(
            request,
            "dashboard/cms/pages/partials/block_list.html",
            {
                "blocks": page.blocks.all(),
                "page": page,
                "block_types": PageBlock.BlockType.choices,
            },
        )
    return redirect("dashboard:page_edit", pk=page.pk)


@dashboard_required
@role_required(User.Role.SUPER_ADMIN, User.Role.ORG_ADMIN, User.Role.SITE_MANAGER)
@require_POST
def block_reorder(request, page_pk):
    org = _org_or_403(request)
    page = get_object_or_404(Page, pk=page_pk, organisation=org)

    if request.content_type == "application/json":
        try:
            data = json.loads(request.body)
            order = data.get("block_order", [])
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON")
    else:
        order = request.POST.getlist("block_order")

    for index, block_id in enumerate(order):
        PageBlock.objects.filter(pk=block_id, page=page).update(order=index)
    return HttpResponse(status=204)


@dashboard_required
@role_required(User.Role.SUPER_ADMIN, User.Role.ORG_ADMIN, User.Role.SITE_MANAGER)
def site_settings_edit(request):
    org = _org_or_403(request)
    settings_obj, _ = SiteSettings.objects.get_or_create(organisation=org)
    if request.method == "POST":
        form = SiteSettingsForm(request.POST, request.FILES, instance=settings_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Site settings saved.")
            return redirect("dashboard:site_settings")
    else:
        form = SiteSettingsForm(instance=settings_obj)
    return render(
        request,
        "dashboard/cms/settings.html",
        {**dashboard_context(request, org), "form": form},
    )


@dashboard_required
@role_required(User.Role.SUPER_ADMIN, User.Role.ORG_ADMIN, User.Role.SITE_MANAGER)
def contact_list(request):
    org = _org_or_403(request)
    contacts = ContactSubmission.objects.filter(organisation=org)
    return render(
        request,
        "dashboard/cms/contacts.html",
        {**dashboard_context(request, org), "contacts": contacts},
    )


# --- Users ---


@dashboard_required
@role_required(User.Role.SUPER_ADMIN, User.Role.ORG_ADMIN)
def user_list(request):
    org = _org_or_403(request)
    users = User.objects.filter(organisation=org) if org else User.objects.all()
    return render(
        request,
        "dashboard/users/list.html",
        {**dashboard_context(request, org), "users": users},
    )


@dashboard_required
@role_required(User.Role.SUPER_ADMIN, User.Role.ORG_ADMIN)
def user_create(request):
    org = _org_or_403(request)
    if request.method == "POST":
        form = UserForm(request.POST)
        password = request.POST.get("password", "changeme123")
        if form.is_valid():
            user = form.save(commit=False)
            if org and not form.cleaned_data.get("organisation"):
                user.organisation = org
            user.set_password(password)
            user.save()
            messages.success(request, "User created.")
            return redirect("dashboard:user_list")
    else:
        form = UserForm(initial={"organisation": org})
    return render(
        request,
        "dashboard/users/form.html",
        {**dashboard_context(request, org), "form": form, "title": "Add User"},
    )


# --- Sites & Terms ---


@dashboard_required
@role_required(User.Role.SUPER_ADMIN, User.Role.ORG_ADMIN)
def site_list(request):
    org = _org_or_403(request)
    sites = Site.objects.filter(organisation=org)
    return render(
        request,
        "dashboard/sites/list.html",
        {**dashboard_context(request, org), "sites": sites},
    )


@dashboard_required
@role_required(User.Role.SUPER_ADMIN, User.Role.ORG_ADMIN)
def site_create(request):
    org = _org_or_403(request)
    if request.method == "POST":
        form = SiteForm(request.POST)
        if form.is_valid():
            site = form.save(commit=False)
            site.organisation = org
            site.save()
            messages.success(request, "Site created.")
            return redirect("dashboard:site_list")
    else:
        form = SiteForm()
    return render(
        request,
        "dashboard/sites/form.html",
        {**dashboard_context(request, org), "form": form, "title": "Add Site"},
    )


# --- Billing ---


@dashboard_required
@role_required(User.Role.SUPER_ADMIN, User.Role.ORG_ADMIN, User.Role.FINANCE)
def billing(request):
    org = _org_or_403(request)
    subscription = getattr(org, "subscription", None) if org else None
    payments = Payment.objects.filter(organisation=org)[:20] if org else []
    return render(
        request,
        "dashboard/billing/index.html",
        {
            **dashboard_context(request, org),
            "subscription": subscription,
            "payments": payments,
        },
    )


@dashboard_required
@role_required(User.Role.SUPER_ADMIN, User.Role.ORG_ADMIN)
def billing_subscribe(request):
    org = _org_or_403(request)
    url = stripe_service.create_org_subscription_checkout(org, request)
    return redirect(url)


@dashboard_required
@role_required(User.Role.SUPER_ADMIN, User.Role.ORG_ADMIN, User.Role.FINANCE)
def billing_success(request):
    messages.success(request, "Subscription updated successfully.")
    return redirect("dashboard:billing")


# --- Finance / Xero ---


@dashboard_required
@role_required(User.Role.SUPER_ADMIN, User.Role.ORG_ADMIN, User.Role.FINANCE)
def finance(request):
    org = _org_or_403(request)
    connection = getattr(org, "xero_connection", None) if org else None
    invoices = XeroInvoice.objects.filter(organisation=org)[:20] if org else []
    return render(
        request,
        "dashboard/finance/index.html",
        {
            **dashboard_context(request, org),
            "xero_connection": connection,
            "invoices": invoices,
        },
    )


@dashboard_required
@role_required(User.Role.SUPER_ADMIN, User.Role.ORG_ADMIN, User.Role.FINANCE)
def xero_connect(request):
    org = _org_or_403(request)
    franchise = getattr(request, "franchise", None)
    state = xero_service.generate_state()
    request.session["xero_oauth_state"] = state
    request.session["xero_org_id"] = org.pk
    if franchise:
        request.session["xero_franchise_slug"] = franchise.slug
    return redirect(xero_service.get_authorization_url(state, franchise=franchise))


@dashboard_required
@role_required(User.Role.SUPER_ADMIN, User.Role.ORG_ADMIN, User.Role.FINANCE)
def xero_callback(request):
    state = request.GET.get("state")
    if state != request.session.get("xero_oauth_state"):
        messages.error(request, "Invalid OAuth state.")
        return redirect("dashboard:finance")

    code = request.GET.get("code")
    org_id = request.session.get("xero_org_id")
    org = get_object_or_404(Organisation, pk=org_id)
    franchise = getattr(request, "franchise", None)

    try:
        tokens = xero_service.exchange_code_for_tokens(code, franchise=franchise)
        xero_service.save_connection(org, tokens)
        messages.success(request, "Xero connected successfully.")
    except Exception as exc:
        messages.error(request, f"Xero connection failed: {exc}")

    return redirect("dashboard:finance")


@dashboard_required
@role_required(User.Role.SUPER_ADMIN, User.Role.ORG_ADMIN, User.Role.FINANCE)
@require_POST
def xero_disconnect(request):
    org = _org_or_403(request)
    XeroConnection.objects.filter(organisation=org).update(
        is_connected=False,
        access_token="",
        refresh_token="",
    )
    messages.success(request, "Xero disconnected.")
    return redirect("dashboard:finance")


@dashboard_required
@role_required(User.Role.SUPER_ADMIN, User.Role.ORG_ADMIN, User.Role.FINANCE)
@require_POST
def sync_payment_to_xero(request, payment_pk):
    org = _org_or_403(request)
    payment = get_object_or_404(Payment, pk=payment_pk, organisation=org)
    invoice = xero_service.create_invoice_for_payment(
        payment, franchise=getattr(request, "franchise", None)
    )
    if invoice.status == XeroInvoice.Status.ERROR:
        messages.error(request, f"Sync failed: {invoice.sync_error}")
    else:
        messages.success(request, "Invoice synced to Xero.")
    return redirect("dashboard:finance")


# --- Stripe webhook ---


@csrf_exempt
def stripe_webhook(request, franchise_slug=None):
    import stripe
    from franchises.context import set_franchise_context
    from franchises.db import register_franchise_database
    from franchises.models import Franchise

    franchise = None
    if franchise_slug:
        try:
            franchise = Franchise.objects.get(slug=franchise_slug, status=Franchise.Status.ACTIVE)
            alias = register_franchise_database(franchise)
            set_franchise_context(franchise, alias)
        except Franchise.DoesNotExist:
            return HttpResponseBadRequest("Unknown franchise")

    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")

    try:
        event = stripe_service.verify_webhook(payload, sig_header, franchise=franchise)
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponseBadRequest()

    if event["type"] == "checkout.session.completed":
        stripe_service.handle_checkout_completed(event["data"]["object"])
        payment_intent = event["data"]["object"]
        from billing.models import Payment

        payment = Payment.objects.filter(
            stripe_checkout_session_id=payment_intent.get("id")
        ).first()
        if payment and payment.status == Payment.Status.SUCCEEDED:
            connection = getattr(payment.organisation, "xero_connection", None)
            if connection and connection.auto_sync_invoices:
                xero_service.create_invoice_for_payment(payment, franchise=franchise)

    return HttpResponse(status=200)


def _default_block_content(block_type):
    defaults = {
        PageBlock.BlockType.HERO: {
            "title": "Welcome to our wraparound care",
            "subtitle": "Safe, fun before and after school clubs",
            "cta_text": "Book a Session",
            "cta_url": "/sessions/",
        },
        PageBlock.BlockType.RICH_TEXT: {
            "body": "<p>Edit this text in the page builder.</p>",
        },
        PageBlock.BlockType.FEATURES: {
            "items": [
                {"title": "Qualified Staff", "description": "DBS-checked, experienced team."},
                {"title": "Flexible Booking", "description": "Book sessions online anytime."},
                {"title": "Healthy Snacks", "description": "Nutritious food included."},
            ],
        },
        PageBlock.BlockType.CTA: {
            "title": "Ready to book?",
            "text": "Register today and secure your child's place.",
            "button_text": "Register Now",
            "button_url": "/accounts/register/",
        },
        PageBlock.BlockType.FAQ: {
            "items": [
                {
                    "question": "What should my child bring?",
                    "answer": "Just themselves! We provide all activities and snacks.",
                },
            ],
        },
        PageBlock.BlockType.TESTIMONIALS: {
            "items": [
                {"quote": "My children love it here!", "author": "Sarah, parent"},
            ],
        },
    }
    return defaults.get(block_type, {})
