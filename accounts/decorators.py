from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest

from accounts.models import User


def role_required(*roles: str):
    def decorator(view_func):
        @login_required
        def wrapper(request: HttpRequest, *args, **kwargs):
            user: User = request.user
            if user.role == User.Role.SUPER_ADMIN:
                return view_func(request, *args, **kwargs)
            if user.role not in roles:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


def dashboard_required(view_func):
    @login_required
    def wrapper(request: HttpRequest, *args, **kwargs):
        if not request.user.is_dashboard_user:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return wrapper


def get_user_organisation(user: User):
    if user.role == User.Role.SUPER_ADMIN:
        return None
    return user.organisation
