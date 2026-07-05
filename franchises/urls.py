from django.urls import path

from franchises import views

app_name = "franchises"

urlpatterns = [
    path("apply/", views.franchise_apply, name="apply"),
    path("apply/thanks/<str:reference>/", views.franchise_apply_thanks, name="apply_thanks"),
    path("application/<str:reference>/", views.franchise_application_status, name="application_status"),
]
