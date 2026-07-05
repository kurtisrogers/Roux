from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from accounts.decorators import dashboard_required
from accounts.forms import LoginForm, ParentRegistrationForm


class UserLoginView(LoginView):
    template_name = "accounts/login.html"
    form_class = LoginForm

    def get_success_url(self):
        if self.request.user.is_dashboard_user:
            return reverse_lazy("dashboard:home")
        return reverse_lazy("public:home")


class UserLogoutView(LogoutView):
    next_page = "public:home"


class ParentRegisterView(CreateView):
    form_class = ParentRegistrationForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("public:home")

    def form_valid(self, form):
        response = super().form_valid(form)
        organisation = getattr(self.request, "organisation", None)
        if organisation:
            self.object.organisation = organisation
            self.object.save(update_fields=["organisation"])
        login(self.request, self.object)
        return response


@dashboard_required
def profile(request):
    return render(request, "accounts/profile.html", {"user_obj": request.user})
