"""BDD steps for programme planner flows."""

from playwright.sync_api import Page, expect
from pytest_bdd import given, parsers, then, when


@when("I open the activities catalogue")
def open_activities(page: Page, app_ready):
    page.goto(app_ready + "/dashboard/programme/activities/")


@when("I open the week packs list")
def open_week_packs(page: Page, app_ready):
    page.goto(app_ready + "/dashboard/programme/week-packs/")


@when("I open the programmes list")
def open_programmes(page: Page, app_ready):
    page.goto(app_ready + "/dashboard/programme/")


@when("I open the closures page")
def open_closures(page: Page, app_ready):
    page.goto(app_ready + "/dashboard/programme/closures/")


@when(parsers.parse('I open week pack "{name}"'))
def open_week_pack(page: Page, name):
    page.get_by_role("link", name=name).click()


@when(parsers.parse('I open programme "{name}"'))
def open_programme(page: Page, name):
    page.get_by_role("link", name=name).click()


@when(parsers.parse('I add activity "{name}" in category "{category}"'))
def add_activity(page: Page, name, category):
    page.get_by_label("Name").fill(name)
    page.get_by_label("Category").select_option(label=category)
    page.get_by_label("Default duration minutes").fill("30")
    page.get_by_role("button", name="Save").click()


@when(parsers.parse('I create week pack "{name}"'))
def create_week_pack(page: Page, name):
    page.get_by_label("Name").fill(name)
    page.get_by_role("button", name="Create").click()


@when("I duplicate the current week pack")
def duplicate_week_pack(page: Page):
    page.get_by_role("button", name="Duplicate pack").click()


@when(parsers.parse('I add a Monday slot from {start} to {end} using activity "{activity}"'))
def add_monday_slot(page: Page, start, end, activity):
    page.get_by_label("Weekday").select_option(label="Monday")
    page.get_by_label("Start time").fill(start)
    page.get_by_label("End time").fill(end)
    page.get_by_label("Activity").select_option(label=activity)
    page.get_by_role("button", name="Add block").click()


@when("I open the programme calendar")
def open_programme_calendar(page: Page):
    page.locator("main").get_by_role("link", name="Calendar", exact=True).click()


@when(parsers.parse('I add closure from "{start}" to "{end}" labelled "{label}"'))
def add_closure(page: Page, start, end, label):
    page.get_by_label("Start date").fill(start)
    page.get_by_label("End date").fill(end)
    page.get_by_label("Label").fill(label)
    page.get_by_role("button", name="Add closure").click()


@when("I open the first programme day editor")
def open_first_day_editor(page: Page):
    page.locator("main").get_by_role("link", name="Edit").first.click()


@when("I replace the programme day with a trip")
def replace_day_with_trip(page: Page):
    page.get_by_label("Action").select_option(label="Replace whole day")
    page.get_by_label("Start time").fill("10:00")
    page.get_by_label("End time").fill("15:00")
    page.get_by_label("Label").fill("Coach trip")
    page.get_by_role("button", name="Save").click()

@when("I start creating a new programme")
def start_new_programme(page: Page):
    page.get_by_role("button", name="New programme").click()


@then(parsers.parse('I should see week label "{label}" on the calendar'))
def see_week_label_on_calendar(page: Page, label):
    expect(page.get_by_text(label).first).to_be_visible()


@then("I should see programme blocks on the day")
def see_programme_blocks(page: Page):
    expect(page.locator("ul li").filter(has_text=":").first).to_be_visible()


@then(parsers.parse('the week pack grid should show "{text}"'))
def week_pack_grid_shows(page: Page, text):
    expect(page.locator(".programme-grid").get_by_text(text).first).to_be_visible()


@then(parsers.parse('the activities table should list "{name}"'))
def activities_table_lists(page: Page, name):
    expect(page.locator("table").get_by_role("cell", name=name)).to_be_visible()


@given("programme seed data exists")
def programme_seed_exists():
    """Seed data is loaded via app_ready / seed_e2e_data fixture."""
