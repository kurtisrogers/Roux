from django.conf import settings
from django.utils.functional import SimpleLazyObject
from organisations.models import Organisation


def _get_organisation(request):
    slug = request.GET.get("org") or getattr(settings, "DEFAULT_ORGANISATION_SLUG", "demo-club")
    host = request.get_host().split(":")[0]

    # Subdomain routing: {slug}.roux.app
    parts = host.split(".")
    if len(parts) > 2 and parts[0] not in ("www", "localhost", "127"):
        slug = parts[0]

    try:
        return Organisation.objects.select_related("site_settings").get(slug=slug, is_active=True)
    except Organisation.DoesNotExist:
        return Organisation.objects.filter(is_active=True).first()


class OrganisationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.organisation = SimpleLazyObject(lambda: _get_organisation(request))
        return self.get_response(request)
