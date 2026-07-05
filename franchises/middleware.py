from django.utils.functional import SimpleLazyObject

from franchises.context import clear_franchise_context, set_franchise_context
from franchises.db import register_franchise_database, resolve_franchise_from_host


class FranchiseMiddleware:
    """Resolve franchise from hostname and set database context."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host()
        franchise = resolve_franchise_from_host(host)

        if franchise:
            db_alias = register_franchise_database(franchise)
            set_franchise_context(franchise, db_alias)
            request.franchise = franchise
        else:
            request.franchise = None

        try:
            return self.get_response(request)
        finally:
            clear_franchise_context()
