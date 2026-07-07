"""Playwright BDD end-to-end tests — scenario registry."""

import pytest
from pytest_bdd import scenarios

import e2e.steps.common_steps  # noqa: F401
import e2e.steps.operations_steps  # noqa: F401
import e2e.steps.parent_steps  # noqa: F401
import e2e.steps.programme_steps  # noqa: F401

pytestmark = pytest.mark.e2e

# Core
scenarios("features/public_site.feature")
scenarios("features/dashboard.feature")
scenarios("features/auth.feature")
scenarios("features/franchise.feature")
# Programme planner
scenarios("features/programme_navigation.feature")
scenarios("features/programme_activities.feature")
scenarios("features/programme_week_packs.feature")
scenarios("features/programme_term.feature")
scenarios("features/programme_closures.feature")
# Operations
scenarios("features/operations_navigation.feature")
scenarios("features/operations_register.feature")
scenarios("features/operations_sidebar.feature")
# Parent journeys
scenarios("features/parent_booking.feature")
scenarios("features/parent_sessions.feature")
scenarios("features/parent_sessions_logged_out.feature")
