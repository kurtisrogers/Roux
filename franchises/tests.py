import pytest

from franchises.context import get_current_db_alias, set_franchise_context
from franchises.db import register_franchise_database, resolve_franchise_from_host
from franchises.models import Franchise, FranchiseDomain
from franchises.services import get_franchise_stripe_config


@pytest.mark.django_db
class TestFranchiseRouting:
    def test_resolve_from_hostname(self):
        franchise = Franchise.objects.create(
            name="North West",
            slug="northwest",
            database_alias="franchise_northwest",
            status=Franchise.Status.ACTIVE,
        )
        FranchiseDomain.objects.create(
            franchise=franchise,
            hostname="northwest.localhost",
            is_primary=True,
        )
        resolved = resolve_franchise_from_host("northwest.localhost")
        assert resolved.slug == "northwest"

    def test_stripe_config_fallback(self):
        config = get_franchise_stripe_config(None)
        assert "secret_key" in config
        assert "publishable_key" in config

    def test_franchise_stripe_config_override(self):
        franchise = Franchise(
            stripe_publishable_key="pk_franchise",
            stripe_secret_key="sk_franchise",
            stripe_webhook_secret="whsec_franchise",
        )
        config = get_franchise_stripe_config(franchise)
        assert config["secret_key"] == "sk_franchise"


@pytest.mark.django_db
class TestFranchiseDatabaseRegistration:
    def test_register_franchise_database_has_full_config(self, settings):
        franchise = Franchise.objects.create(
            name="Test",
            slug="regtest",
            database_alias="franchise_regtest",
            status=Franchise.Status.ACTIVE,
        )
        alias = register_franchise_database(franchise)
        assert alias == "franchise_regtest"
        assert "TIME_ZONE" in settings.DATABASES[alias]
        assert settings.DATABASES[alias]["ENGINE"]

    def test_context_switches_db_alias(self, settings):
        franchise = Franchise.objects.create(
            name="Ctx",
            slug="ctxtest",
            database_alias="franchise_ctxtest",
            status=Franchise.Status.ACTIVE,
        )
        register_franchise_database(franchise)
        set_franchise_context(franchise, franchise.database_alias)
        assert get_current_db_alias() == "franchise_ctxtest"
