from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from api.views import BookingViewSet, ChildViewSet, MeView, SessionViewSet

router = DefaultRouter()
router.register("children", ChildViewSet, basename="child")
router.register("sessions", SessionViewSet, basename="session")
router.register("bookings", BookingViewSet, basename="booking")

urlpatterns = [
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", MeView.as_view(), name="me"),
    path("", include(router.urls)),
]
