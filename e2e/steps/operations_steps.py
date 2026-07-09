"""BDD steps for operations module flows."""

from playwright.sync_api import Page, expect
from pytest_bdd import then, when


@when("I open the waitlist page")
def open_waitlist(page: Page, app_ready):
    page.goto(app_ready + "/dashboard/waitlist/")


@when("I open the recurring bookings page")
def open_recurring(page: Page, app_ready):
    page.goto(app_ready + "/dashboard/recurring/")


@when("I open the childcare vouchers page")
def open_vouchers(page: Page, app_ready):
    page.goto(app_ready + "/dashboard/vouchers/")


@when("I open the voucher redeem page")
def open_voucher_redeem(page: Page, app_ready):
    page.goto(app_ready + "/dashboard/vouchers/redeem/")


@when("I open the subsidies page")
def open_subsidies(page: Page, app_ready):
    page.goto(app_ready + "/dashboard/subsidies/")


@when("I open the payment plans page")
def open_payment_plans(page: Page, app_ready):
    page.goto(app_ready + "/dashboard/payment-plans/")


@when("I open the analytics dashboard")
def open_analytics(page: Page, app_ready):
    page.goto(app_ready + "/dashboard/analytics/")


@when("I open the staff rota page")
def open_rota(page: Page, app_ready):
    page.goto(app_ready + "/dashboard/rota/")


@when("I open the visitors log")
def open_visitors(page: Page, app_ready):
    page.goto(app_ready + "/dashboard/visitors/")


@when("I open the medication log")
def open_medication(page: Page, app_ready):
    page.goto(app_ready + "/dashboard/medication/")


@when("I open staff compliance")
def open_compliance(page: Page, app_ready):
    page.goto(app_ready + "/dashboard/compliance/")


@when("I open safeguarding cases")
def open_safeguarding(page: Page, app_ready):
    page.goto(app_ready + "/dashboard/safeguarding/")


@when("I open bulk session generator")
def open_bulk_sessions(page: Page, app_ready):
    page.goto(app_ready + "/dashboard/sessions/bulk/")


@when("I open the booking calendar")
def open_booking_calendar(page: Page, app_ready):
    page.goto(app_ready + "/dashboard/calendar/")


@when("I open the after-school session register")
def open_after_school_register(page: Page, app_ready):
    page.goto(app_ready + "/dashboard/sessions/")
    page.get_by_role("row").filter(has_text="After School Club").first.get_by_role(
        "link", name="Manage"
    ).click()
    page.get_by_role("button", name="Open Register").click()


@when("I open the after-school session detail")
def open_after_school_detail(page: Page, app_ready):
    page.goto(app_ready + "/dashboard/sessions/")
    page.get_by_role("row").filter(has_text="After School Club").first.get_by_role(
        "link", name="Manage"
    ).click()


@when("I open the walk-in booking form for the first session")
def open_walk_in(page: Page, app_ready):
    page.goto(app_ready + "/dashboard/sessions/")
    session_row = page.get_by_role("row").filter(has_text="After School Club").first
    manage_href = session_row.get_by_role("link", name="Manage").get_attribute("href")
    session_pk = manage_href.rstrip("/").split("/")[-1]
    page.goto(app_ready + f"/dashboard/sessions/{session_pk}/walk-in/")


@then("I should see the programme run sheet")
def see_programme_run_sheet(page: Page):
    expect(page.get_by_text("Today's programme")).to_be_visible()


@then("I should see snack time on the register programme")
def see_snack_on_register(page: Page):
    expect(page.locator("summary").filter(has_text="Today's programme")).to_be_visible()
    expect(page.get_by_text("Snack time").first).to_be_visible()


@then("I should see today's programme on the session page")
def see_programme_on_session(page: Page):
    expect(page.locator("summary").filter(has_text="Today's programme")).to_be_visible()
