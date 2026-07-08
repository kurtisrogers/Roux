"""Shared Playwright BDD step definitions."""

import re

import pytest
from playwright.sync_api import Page, expect
from pytest_bdd import given, parsers, then, when

pytestmark = pytest.mark.e2e


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


@given(parsers.parse('I am logged in as "{username}" with password "{password}"'))
def logged_in(page: Page, app_ready, username, password):
    page.goto(app_ready + "/accounts/login/")
    page.get_by_placeholder("Email or username").fill(username)
    page.get_by_placeholder("Password").fill(password)
    page.get_by_role("button", name="Login").click()


@given("I am logged in as admin")
def logged_in_as_admin(page: Page, app_ready):
    page.goto(app_ready + "/accounts/login/")
    page.get_by_placeholder("Email or username").fill("admin")
    page.get_by_placeholder("Password").fill("admin123")
    page.get_by_role("button", name="Login").click()


@given("I am logged in as a parent")
def logged_in_as_parent(page: Page, app_ready):
    page.goto(app_ready + "/accounts/login/")
    page.get_by_placeholder("Email or username").fill("parent1")
    page.get_by_placeholder("Password").fill("parent123")
    page.get_by_role("button", name="Login").click()


@when(parsers.parse('I click "{text}"'))
def click_text(page: Page, text):
    link = page.get_by_role("link", name=text)
    if link.count() > 0:
        link.first.click()
    else:
        page.get_by_role("button", name=text).first.click()


@when(parsers.parse('I click the button "{text}"'))
def click_button(page: Page, text):
    page.get_by_role("button", name=text).click()


@when(parsers.parse('I fill in "{field}" with "{value}"'))
def fill_field(page: Page, field, value):
    page.get_by_label(field).fill(value)


@when(parsers.parse('I select "{value}" from "{field}"'))
def select_field(page: Page, value, field):
    page.get_by_label(field).select_option(label=value)


@when(parsers.parse('I press "{text}"'))
def press_button(page: Page, text):
    page.get_by_role("button", name=text).click()


@when("I submit the login form")
def submit_login(page: Page):
    page.get_by_role("button", name="Login").click()


@when(parsers.parse('I navigate to "{path}"'))
def navigate_to(page: Page, app_ready, path):
    page.goto(app_ready + path)


@then(parsers.parse('I should see "{text}"'))
def should_see(page: Page, text):
    expect(page.locator(":visible").filter(has_text=text).first).to_be_visible()


@then(parsers.parse('I should see heading "{text}"'))
def should_see_heading(page: Page, text):
    expect(page.get_by_role("heading", name=text).first).to_be_visible()


@then(parsers.parse('the page title should contain "{text}"'))
def title_contains(page: Page, text):
    expect(page).to_have_title(re.compile(re.escape(text)))


@then(parsers.parse('the table should contain "{text}"'))
def table_contains(page: Page, text):
    expect(page.locator("table").get_by_text(text).first).to_be_visible()


@then(parsers.parse('I should not see "{text}"'))
def should_not_see(page: Page, text):
    expect(page.get_by_text(text)).to_have_count(0)
