import pytest
from franchises.context import clear_franchise_context


@pytest.fixture(autouse=True)
def reset_franchise_context():
    yield
    clear_franchise_context()


@pytest.fixture
def seed_e2e_data(db):
    from django.core.management import call_command

    call_command("seed_demo")
