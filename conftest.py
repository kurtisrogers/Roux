import pytest


@pytest.fixture
def seed_e2e_data(db):
    from django.core.management import call_command

    call_command("seed_demo")
