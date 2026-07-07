"""BDD steps for parent-facing journeys."""

import re

from playwright.sync_api import Page, expect
from pytest_bdd import then, when


@when("I browse available sessions")
def browse_sessions(page: Page, app_ready):
    page.goto(app_ready + "/sessions/")


@when("I open the parent booking calendar")
def parent_calendar(page: Page, app_ready):
    page.goto(app_ready + "/sessions/calendar/")


@when("I open the report absence page")
def report_absence(page: Page, app_ready):
    page.goto(app_ready + "/absence/")


@when("I open my bookings")
def my_bookings(page: Page, app_ready):
    page.goto(app_ready + "/my-bookings/")


@when("I click login to book on the first session")
def click_login_to_book(page: Page):
    page.locator("a[role=button]", has_text="Login to Book").first.click(force=True)


@when("I open the first after-school booking page")
def open_after_school_booking(page: Page, app_ready):
    page.goto(app_ready + "/sessions/")
    book_link = (
        page.get_by_role("article")
        .filter(has_text="After School Club")
        .locator('a[href*="/book/"]')
        .first
    )
    href = book_link.get_attribute("href")
    assert href, "Expected a book link for After School Club"
    page.goto(href if href.startswith("http") else app_ready + href)


@then("I should see planned activities for the session")
def see_planned_activities(page: Page):
    expect(page.get_by_role("heading", name="Planned activities")).to_be_visible()
    expect(page.locator(":visible").filter(has_text="Snack time").first).to_be_visible()


@then("I should see the childcare voucher payment option")
def see_voucher_payment(page: Page):
    expect(page.get_by_text("Childcare voucher")).to_be_visible()


@then("I should see the absence reporting form")
def see_absence_form(page: Page):
    expect(page.get_by_role("heading", name=re.compile("Report absence", re.I))).to_be_visible()
