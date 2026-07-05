from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import dashboard_required, role_required
from accounts.models import User
from dashboard.mixins import dashboard_context
from franchises.forms import FranchiseForm, FranchiseIntegrationForm
from franchises.models import Franchise
from franchises.services import provision_franchise


@dashboard_required
@role_required(User.Role.SUPER_ADMIN)
def franchise_list(request):
    franchises = Franchise.objects.all()
    return render(
        request,
        "dashboard/franchises/list.html",
        {**dashboard_context(request, None), "franchises": franchises},
    )


@dashboard_required
@role_required(User.Role.SUPER_ADMIN)
def franchise_create(request):
    if request.method == "POST":
        form = FranchiseForm(request.POST)
        if form.is_valid():
            franchise = provision_franchise(
                name=form.cleaned_data["name"],
                slug=form.cleaned_data["slug"],
                contact_email=form.cleaned_data.get("contact_email", ""),
                hostname=form.cleaned_data.get("hostname", ""),
            )
            franchise.stripe_publishable_key = form.cleaned_data.get("stripe_publishable_key", "")
            franchise.stripe_secret_key = form.cleaned_data.get("stripe_secret_key", "")
            franchise.stripe_webhook_secret = form.cleaned_data.get("stripe_webhook_secret", "")
            franchise.xero_client_id = form.cleaned_data.get("xero_client_id", "")
            franchise.xero_client_secret = form.cleaned_data.get("xero_client_secret", "")
            franchise.xero_redirect_uri = form.cleaned_data.get("xero_redirect_uri", "")
            franchise.default_from_email = form.cleaned_data.get("default_from_email", "")
            franchise.save()
            messages.success(
                request,
                f"Franchise '{franchise.name}' provisioned with isolated database.",
            )
            return redirect("dashboard:franchise_detail", pk=franchise.pk)
    else:
        form = FranchiseForm()
    return render(
        request,
        "dashboard/franchises/form.html",
        {**dashboard_context(request, None), "form": form, "title": "New Franchise"},
    )


@dashboard_required
@role_required(User.Role.SUPER_ADMIN)
def franchise_detail(request, pk):
    franchise = get_object_or_404(Franchise, pk=pk)
    primary_domain = franchise.domains.filter(is_primary=True).first()
    return render(
        request,
        "dashboard/franchises/detail.html",
        {
            **dashboard_context(request, None),
            "franchise": franchise,
            "primary_domain": primary_domain,
        },
    )


@dashboard_required
@role_required(User.Role.SUPER_ADMIN)
def franchise_integrations(request, pk):
    franchise = get_object_or_404(Franchise, pk=pk)
    if request.method == "POST":
        form = FranchiseIntegrationForm(request.POST, instance=franchise)
        if form.is_valid():
            form.save()
            messages.success(request, "Integration settings saved.")
            return redirect("dashboard:franchise_detail", pk=franchise.pk)
    else:
        form = FranchiseIntegrationForm(instance=franchise)
    return render(
        request,
        "dashboard/franchises/integrations.html",
        {**dashboard_context(request, None), "franchise": franchise, "form": form},
    )
