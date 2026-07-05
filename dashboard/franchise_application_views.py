from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import dashboard_required, role_required
from accounts.models import User
from dashboard.mixins import dashboard_context
from franchises.application_services import set_application_status
from franchises.forms import FranchiseApplicationReviewForm
from franchises.models import FranchiseApplication


@dashboard_required
@role_required(User.Role.SUPER_ADMIN)
def application_list(request):
    status_filter = request.GET.get("status", "")
    applications = FranchiseApplication.objects.select_related("franchise")
    if status_filter:
        applications = applications.filter(status=status_filter)
    return render(
        request,
        "dashboard/franchise_applications/list.html",
        {
            **dashboard_context(request, None),
            "applications": applications,
            "status_filter": status_filter,
            "status_choices": FranchiseApplication.Status.choices,
        },
    )


@dashboard_required
@role_required(User.Role.SUPER_ADMIN)
def application_detail(request, pk):
    application = get_object_or_404(FranchiseApplication.objects.select_related("franchise"), pk=pk)
    if request.method == "POST":
        form = FranchiseApplicationReviewForm(request.POST, instance=application)
        if form.is_valid():
            application = set_application_status(
                application,
                form.cleaned_data["status"],
                admin_notes=form.cleaned_data.get("admin_notes", ""),
            )
            messages.success(request, f"Application updated to {application.get_status_display()}.")
            return redirect("dashboard:franchise_application_detail", pk=application.pk)
    else:
        form = FranchiseApplicationReviewForm(instance=application)

    return render(
        request,
        "dashboard/franchise_applications/detail.html",
        {
            **dashboard_context(request, None),
            "application": application,
            "form": form,
        },
    )
