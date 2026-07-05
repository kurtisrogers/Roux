from django.urls import path

from accounts import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.UserLoginView.as_view(), name="login"),
    path("logout/", views.UserLogoutView.as_view(), name="logout"),
    path("register/", views.ParentRegisterView.as_view(), name="register"),
    path("profile/", views.profile, name="profile"),
]
