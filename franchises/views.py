from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from franchises.application_services import submit_franchise_application
from franchises.forms import FranchiseApplicationForm
from franchises.models import FranchiseApplication


def franchise_apply(request):
    """Public franchise partner application signup journey."""
    if request.method == "POST":
        form = FranchiseApplicationForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            application = submit_franchise_application(
                applicant_name=data["applicant_name"],
                business_name=data["business_name"],
                email=data["email"],
                phone=data.get("phone", ""),
                region=data.get("region", ""),
                experience_years=data.get("experience_years"),
                message=data.get("message", ""),
            )
            messages.success(
                request,
                "Thank you — we've received your application and sent a confirmation email.",
            )
            return redirect("franchises:apply_thanks", reference=application.reference)
    else:
        form = FranchiseApplicationForm()

    return render(
        request,
        "franchises/apply.html",
        {"form": form, "status_choices": FranchiseApplication.Status.choices},
    )


def franchise_apply_thanks(request, reference):
    application = get_object_or_404(FranchiseApplication, reference=reference)
    return render(
        request,
        "franchises/apply_thanks.html",
        {"application": application},
    )


def franchise_application_status(request, reference):
    application = get_object_or_404(FranchiseApplication, reference=reference)
    return render(
        request,
        "franchises/application_status.html",
        {"application": application},
    )
