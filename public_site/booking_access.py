from bookings.models import Booking
from django.http import Http404
from django.shortcuts import get_object_or_404


def booking_for_request(request, pk: int, *, require_owner: bool = False) -> Booking:
    """Return a booking scoped to the current organisation and optional owner."""
    organisation = getattr(request, "organisation", None)
    if organisation is None:
        raise Http404("No organisation context")

    filters = {"pk": pk, "session__organisation": organisation}
    if require_owner:
        if not request.user.is_authenticated:
            raise Http404("Authentication required")
        filters["booked_by"] = request.user

    return get_object_or_404(Booking, **filters)
