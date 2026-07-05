from accounts.models import User
from bookings.models import Booking, Child, Session
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import (
    BookingSerializer,
    ChildSerializer,
    OrganisationSerializer,
    SessionSerializer,
    UserSerializer,
)


class IsParentOrStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated


class OrganisationScopedMixin:
    def get_organisation(self):
        user = self.request.user
        if user.role == User.Role.SUPER_ADMIN:
            org_id = self.request.query_params.get("organisation")
            if org_id:
                from organisations.models import Organisation

                return Organisation.objects.filter(pk=org_id).first()
        return user.organisation


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        data = UserSerializer(request.user).data
        if request.user.organisation:
            data["organisation"] = OrganisationSerializer(request.user.organisation).data
        return Response(data)


class ChildViewSet(viewsets.ModelViewSet):
    serializer_class = ChildSerializer
    permission_classes = [IsParentOrStaff]

    def get_queryset(self):
        user = self.request.user
        if user.role == User.Role.PARENT:
            return Child.objects.filter(parent=user, is_active=True)
        if user.organisation:
            return Child.objects.filter(organisation=user.organisation, is_active=True)
        return Child.objects.none()


class SessionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Session.objects.filter(status=Session.Status.SCHEDULED)
        if user.organisation:
            qs = qs.filter(organisation=user.organisation)
        return qs.select_related("session_type", "site").order_by("date", "start_time")

    @action(detail=False, methods=["get"])
    def upcoming(self, request):
        from django.utils import timezone

        qs = self.get_queryset().filter(date__gte=timezone.now().date())[:20]
        return Response(self.get_serializer(qs, many=True).data)


class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [IsParentOrStaff]
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        user = self.request.user
        qs = Booking.objects.select_related(
            "child", "session", "session__session_type", "session__site"
        )
        if user.role == User.Role.PARENT:
            return qs.filter(booked_by=user)
        if user.organisation:
            return qs.filter(session__organisation=user.organisation)
        return qs.none()

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        if booking.status in (Booking.Status.CANCELLED, Booking.Status.CHECKED_OUT):
            return Response({"detail": "Cannot cancel."}, status=400)
        booking.status = Booking.Status.CANCELLED
        booking.save(update_fields=["status"])
        return Response(BookingSerializer(booking).data)
