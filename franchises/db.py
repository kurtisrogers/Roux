import os
import re
from pathlib import Path
from urllib.parse import urlparse

from django.conf import settings
from django.db import connections

from franchises.context import get_tenant_db_alias
from franchises.models import Franchise, FranchiseDomain

CONTROL_PLANE_MODELS = {
    "franchises.franchise",
    "franchises.franchisedomain",
    "franchises.franchiseapplication",
}


class FranchiseRouter:
    """Route control-plane models to default; tenant models to franchise DB."""

    def db_for_read(self, model, **hints):
        if model._meta.label_lower in CONTROL_PLANE_MODELS:
            return "default"
        return get_tenant_db_alias()

    def db_for_write(self, model, **hints):
        if model._meta.label_lower in CONTROL_PLANE_MODELS:
            return "default"
        return get_tenant_db_alias()

    def allow_relation(self, obj1, obj2, **hints):
        db1 = obj1._state.db or "default"
        db2 = obj2._state.db or "default"
        if db1 == db2:
            return True
        # Never allow relations between control plane and tenant DBs
        models = {obj1._meta.label_lower, obj2._meta.label_lower}
        if models & CONTROL_PLANE_MODELS:
            return False
        return db1 == db2

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == "franchises":
            return db == "default"
        if db == "default":
            # Tenant apps can migrate on default for legacy single-tenant installs
            return True
        if db.startswith("franchise_"):
            return app_label != "franchises"
        return None


def parse_database_url(url: str) -> dict:
    match = re.match(
        r"postgres(?:ql)?://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)",
        url,
    )
    if not match:
        raise ValueError(f"Invalid database URL: {url}")
    user, password, host, port, name = match.groups()
    return {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": name,
        "USER": user,
        "PASSWORD": password,
        "HOST": host,
        "PORT": port,
    }


def register_franchise_database(franchise: Franchise) -> str:
    """Register franchise database in Django settings at runtime."""
    alias = franchise.database_alias
    if alias in settings.DATABASES:
        return alias

    base_config = settings.DATABASES["default"].copy()

    if franchise.database_url:
        config = {**base_config, **parse_database_url(franchise.database_url)}
    else:
        db_dir = Path(settings.BASE_DIR) / "data" / "franchises"
        db_dir.mkdir(parents=True, exist_ok=True)
        config = {
            **base_config,
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": db_dir / f"{franchise.slug}.sqlite3",
        }

    settings.DATABASES[alias] = config
    connections.databases[alias] = config
    return alias


def franchise_database_name(slug: str) -> str:
    return f"roux_franchise_{slug.replace('-', '_')}"


def build_franchise_database_url(slug: str, *, db_name: str | None = None) -> str:
    """Build PostgreSQL URL for a franchise database from the platform template."""
    template = os.getenv("FRANCHISE_DATABASE_URL_TEMPLATE", "")
    if not template:
        return ""
    name = db_name or franchise_database_name(slug)
    return template.replace("{db_name}", name)


def create_franchise_database(db_name: str) -> None:
    """Create a PostgreSQL database on the shared cluster (production only)."""
    template = os.getenv("FRANCHISE_DATABASE_URL_TEMPLATE", "")
    if not template:
        return

    admin_url = os.getenv("DATABASE_URL", "")
    if not admin_url or not admin_url.startswith("postgres"):
        return

    try:
        import psycopg
        from psycopg import sql
    except ImportError:
        return

    parsed = urlparse(admin_url)
    conninfo = (
        f"host={parsed.hostname} port={parsed.port or 5432} "
        f"user={parsed.username} password={parsed.password} dbname=postgres"
    )
    with psycopg.connect(conninfo, autocommit=True) as conn, conn.cursor() as cur:
        cur.execute(
            sql.SQL("SELECT 1 FROM pg_database WHERE datname = {}").format(sql.Literal(db_name))
        )
        if cur.fetchone():
            return
        cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))


def resolve_franchise_from_host(host: str) -> Franchise | None:
    host = host.split(":")[0].lower()

    try:
        domain = FranchiseDomain.objects.select_related("franchise").get(
            hostname=host,
            franchise__status=Franchise.Status.ACTIVE,
        )
        return domain.franchise
    except FranchiseDomain.DoesNotExist:
        pass

    parts = host.split(".")
    if len(parts) >= 2 and parts[0] not in ("www", "app", "staging", "localhost", "127"):
        slug = parts[0]
        try:
            return Franchise.objects.get(slug=slug, status=Franchise.Status.ACTIVE)
        except Franchise.DoesNotExist:
            return None
    return None
