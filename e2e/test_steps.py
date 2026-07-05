"""Playwright BDD end-to-end tests."""

import re

import pytest
from playwright.sync_api import Page, expect
from pytest_bdd import given, parsers, scenarios, then, when

pytestmark = pytest.mark.e2e

scenarios("features/public_site.feature")
scenarios("features/dashboard.feature")
scenarios("features/auth.feature")


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {**browser_context_args, "viewport": {"width": 1280, "height": 720}}


@pytest.fixture
def app_ready(live_server, seed_e2e_data):
    return live_server.url


@given("the application is running")
def application_running(app_ready):
    assert app_ready


@given("I am on the homepage")
def on_homepage(page: Page, app_ready):
    page.goto(app_ready + "/")


@given(parsers.parse('I visit "{path}"'))
def visit_path(page: Page, app_ready, path):
    page.goto(app_ready + path)


@when(parsers.parse('I click "{text}"'))
def click_text(page: Page, text):
    page.get_by_role("link", name=text).first.click()


@when(parsers.parse('I fill in "{field}" with "{value}"'))
def fill_field(page: Page, field, value):
    page.get_by_label(field).fill(value)


@when("I submit the login form")
def submit_login(page: Page):
    page.get_by_role("button", name="Login").click()


@then(parsers.parse('I should see "{text}"'))
def should_see(page: Page, text):
    expect(page.get_by_text(text).first).to_be_visible()


@then(parsers.parse('the page title should contain "{text}"'))
def title_contains(page: Page, text):
    expect(page).to_have_title(re.compile(re.escape(text)))


@given(parsers.parse('I am logged in as "{username}" with password "{password}"'))
def logged_in(page: Page, app_ready, username, password):
    page.goto(app_ready + "/accounts/login/")
    page.get_by_placeholder("Email or username").fill(username)
    page.get_by_placeholder("Password").fill(password)
    page.get_by_role("button", name="Login").click()


@when(parsers.parse('I navigate to "{path}"'))
def navigate_to(page: Page, app_ready, path):
    page.goto(app_ready + path)
