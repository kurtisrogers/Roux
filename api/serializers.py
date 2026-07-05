from rest_framework import serializers

from accounts.models import User
from bookings.models import Booking, Child, Session, SessionType
from organisations.models import Organisation, Site


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "phone", "role")
        read_only_fields = fields


class OrganisationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organisation
        fields = ("id", "name", "slug", "email", "phone", "city", "postcode")


class SiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = ("id", "name", "slug", "city", "postcode", "capacity")


class ChildSerializer(serializers.ModelSerializer):
    age = serializers.IntegerField(read_only=True)
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = Child
        fields = (
            "id",
            "first_name",
            "last_name",
            "full_name",
            "date_of_birth",
            "age",
            "school_year",
            "allergies",
            "medical_notes",
            "dietary_requirements",
            "emergency_contact_name",
            "emergency_contact_phone",
            "photo_consent",
            "is_active",
        )
        read_only_fields = ("id",)

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["parent"] = request.user
        validated_data["organisation"] = request.user.organisation
        return super().create(validated_data)


class SessionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionType
        fields = (
            "id",
            "name",
            "category",
            "description",
            "price",
            "capacity",
            "age_min",
            "age_max",
        )


class SessionSerializer(serializers.ModelSerializer):
    session_type = SessionTypeSerializer(read_only=True)
    site = SiteSerializer(read_only=True)
    booked_count = serializers.IntegerField(read_only=True)
    spaces_remaining = serializers.IntegerField(read_only=True)
    is_full = serializers.BooleanField(read_only=True)

    class Meta:
        model = Session
        fields = (
            "id",
            "session_type",
            "site",
            "date",
            "start_time",
            "end_time",
            "status",
            "booked_count",
            "spaces_remaining",
            "is_full",
        )


class BookingSerializer(serializers.ModelSerializer):
    child = ChildSerializer(read_only=True)
    child_id = serializers.PrimaryKeyRelatedField(
        queryset=Child.objects.all(),
        source="child",
        write_only=True,
    )
    session = SessionSerializer(read_only=True)
    session_id = serializers.PrimaryKeyRelatedField(
        queryset=Session.objects.all(),
        source="session",
        write_only=True,
    )
    price = serializers.DecimalField(max_digits=8, decimal_places=2, read_only=True)

    class Meta:
        model = Booking
        fields = (
            "id",
            "child",
            "child_id",
            "session",
            "session_id",
            "status",
            "payment_status",
            "special_requirements",
            "price",
            "created_at",
        )
        read_only_fields = ("id", "status", "payment_status", "created_at")

    def validate_child_id(self, child):
        request = self.context["request"]
        if child.parent_id != request.user.id:
            raise serializers.ValidationError("Child does not belong to you.")
        return child

    def validate_session_id(self, session):
        request = self.context["request"]
        if session.organisation_id != request.user.organisation_id:
            raise serializers.ValidationError("Session not available.")
        if session.is_full:
            raise serializers.ValidationError("Session is full.")
        return session

    def create(self, validated_data):
        validated_data["booked_by"] = self.context["request"].user
        return super().create(validated_data)
