"""Dashboard view helpers and mixins."""

from accounts.decorators import get_user_organisation
from accounts.models import User


def resolve_organisation(request, organisation=None):
    """Return the organisation scoped to the current user."""
    if organisation:
        return organisation
    if request.user.role == User.Role.SUPER_ADMIN:
        org_id = request.GET.get("org")
        if org_id:
            from organisations.models import Organisation

            return Organisation.objects.filter(pk=org_id).first()
        return getattr(request, "organisation", None)
    return get_user_organisation(request.user)


def dashboard_context(request, organisation=None):
    org = resolve_organisation(request, organisation)
    return {
        "organisation": org,
        "is_super_admin": request.user.role == User.Role.SUPER_ADMIN,
    }
