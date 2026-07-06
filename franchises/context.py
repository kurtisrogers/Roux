"""Thread-local franchise database context."""

from contextvars import ContextVar

_current_franchise = ContextVar("current_franchise", default=None)
_current_db_alias = ContextVar("current_db_alias", default="default")


def set_franchise_context(franchise, db_alias: str) -> None:
    _current_franchise.set(franchise)
    _current_db_alias.set(db_alias)


def clear_franchise_context() -> None:
    _current_franchise.set(None)
    _current_db_alias.set("default")


def get_current_franchise():
    return _current_franchise.get()


def get_current_db_alias() -> str:
    return _current_db_alias.get() or "default"


def get_tenant_db_alias() -> str:
    """Database alias for tenant-scoped models."""
    return get_current_db_alias()
