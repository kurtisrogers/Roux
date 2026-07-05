from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from billing.services import stripe_service
from bookings.models import Booking, Child, Session
from cms.block_renderer import render_block
from cms.models import Page
from dashboard.forms import ChildForm, ContactForm


def home(request):
    organisation = request.organisation
    if not organisation:
        return render(request, "public/no_org.html")

    page = Page.objects.filter(
        organisation=organisation, is_homepage=True, is_published=True
    ).first()
    if not page:
        page = Page.objects.filter(
            organisation=organisation, is_published=True
        ).first()

    blocks = []
    if page:
        blocks = [
            render_block(b, organisation, request)
            for b in page.blocks.filter(is_visible=True)
        ]

    return render(
        request,
        "public/home.html",
        {"page": page, "rendered_blocks": blocks},
    )


def page_detail(request, slug):
    organisation = request.organisation
    page = get_object_or_404(
        Page, organisation=organisation, slug=slug, is_published=True
    )
    blocks = [
        render_block(b, organisation, request)
        for b in page.blocks.filter(is_visible=True)
    ]
    return render(
        request,
        "public/page.html",
        {"page": page, "rendered_blocks": blocks},
    )


def session_list(request):
    organisation = request.organisation
    sessions = (
        Session.objects.filter(
            organisation=organisation,
            status=Session.Status.SCHEDULED,
        )
        .select_related("session_type", "site")
        .order_by("date", "start_time")
    )
    return render(request, "public/sessions.html", {"sessions": sessions})


@login_required
def book_session(request, pk):
    organisation = request.organisation
    session = get_object_or_404(
        Session, pk=pk, organisation=organisation, status=Session.Status.SCHEDULED
    )
    children = Child.objects.filter(
        parent=request.user, organisation=organisation, is_active=True
    )

    if request.method == "POST":
        child_id = request.POST.get("child")
        child = get_object_or_404(Child, pk=child_id, parent=request.user)
        if session.is_full:
            messages.error(request, "This session is full.")
            return redirect("public:session_list")

        booking, created = Booking.objects.get_or_create(
            child=child,
            session=session,
            defaults={
                "booked_by": request.user,
                "status": Booking.Status.PENDING,
                "special_requirements": request.POST.get("special_requirements", ""),
            },
        )
        if not created:
            messages.warning(request, "Already booked for this session.")
            return redirect("public:my_bookings")

        checkout_url = stripe_service.create_booking_checkout_session(booking, request)
        return redirect(checkout_url)

    return render(
        request,
        "public/book.html",
        {"session": session, "children": children, "child_form": ChildForm()},
    )


@login_required
def my_bookings(request):
    bookings = (
        Booking.objects.filter(booked_by=request.user)
        .select_related("child", "session", "session__session_type", "session__site")
        .order_by("-session__date")
    )
    return render(request, "public/my_bookings.html", {"bookings": bookings})


@login_required
def add_child(request):
    organisation = request.organisation
    if request.method == "POST":
        form = ChildForm(request.POST)
        if form.is_valid():
            child = form.save(commit=False)
            child.parent = request.user
            child.organisation = organisation
            child.save()
            messages.success(request, f"Added {child.full_name}.")
            return redirect("public:my_bookings")
    else:
        form = ChildForm()
    return render(request, "public/add_child.html", {"form": form})


def booking_success(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    return render(request, "public/booking_success.html", {"booking": booking})


def booking_cancel(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    booking.status = Booking.Status.CANCELLED
    booking.save(update_fields=["status"])
    messages.info(request, "Booking cancelled.")
    return redirect("public:session_list")


def contact_form(request):
    organisation = request.organisation
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.organisation = organisation
            submission.save()
            if request.htmx:
                return HttpResponse(
                    '<p class="success">Thank you! We\'ll be in touch soon.</p>'
                )
            messages.success(request, "Message sent.")
            return redirect("public:home")
    else:
        form = ContactForm()
    return render(request, "public/partials/contact_form.html", {"form": form})
