#!/usr/bin/env python
"""Capture landing page screenshots from a running Roux instance."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import django

ROOT = Path(__file__).resolve().parents[1]
SCREENSHOT_DIR = ROOT / "landing" / "assets" / "screenshots"


def setup_django() -> None:
    sys.path.insert(0, str(ROOT))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()


def resolve_urls() -> dict[str, str]:
    from bookings.models import Session
    from programme.models import Programme

    programme = Programme.objects.order_by("-id").first()
    programme_pk = programme.pk if programme else 1

    register_session = (
        Session.objects.filter(session_type__name__icontains="breakfast")
        .order_by("date")
        .first()
    )
    if not register_session:
        register_session = Session.objects.order_by("date").first()

    book_session = (
        Session.objects.filter(session_type__name__icontains="breakfast")
        .order_by("date")
        .first()
    )
    if not book_session:
        book_session = Session.objects.order_by("date").first()

    register_pk = register_session.pk if register_session else 1
    book_pk = book_session.pk if book_session else 1

    return {
        "dashboard_home": "/dashboard/",
        "session_register": f"/dashboard/sessions/{register_pk}/register/",
        "programme_calendar": f"/dashboard/programme/{programme_pk}/calendar/",
        "ofsted_dashboard": "/dashboard/ofsted/",
        "operations_analytics": "/dashboard/analytics/",
        "parent_sessions": "/sessions/",
        "parent_booking": f"/sessions/{book_pk}/book/",
        "public_homepage": "/",
    }


def login(page, base_url: str, username: str, password: str) -> None:
    page.goto(f"{base_url}/accounts/login/")
    page.get_by_placeholder("Email or username").fill(username)
    page.get_by_placeholder("Password").fill(password)
    page.get_by_role("button", name="Login").click()
    page.wait_for_load_state("networkidle")


def capture(base_url: str) -> None:
    from playwright.sync_api import sync_playwright

    urls = resolve_urls()
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

    shots = [
        ("dashboard-home.png", urls["dashboard_home"], "admin", "admin123", {"width": 1280, "height": 800}),
        ("session-register.png", urls["session_register"], "staff1", "staff123", {"width": 1280, "height": 900}),
        ("programme-calendar.png", urls["programme_calendar"], "admin", "admin123", {"width": 1280, "height": 800}),
        ("ofsted-dashboard.png", urls["ofsted_dashboard"], "admin", "admin123", {"width": 1280, "height": 800}),
        ("operations-analytics.png", urls["operations_analytics"], "admin", "admin123", {"width": 1280, "height": 800}),
        ("parent-sessions.png", urls["parent_sessions"], "parent1", "parent123", {"width": 390, "height": 844}),
        ("parent-booking.png", urls["parent_booking"], "parent1", "parent123", {"width": 390, "height": 844}),
        ("public-homepage.png", urls["public_homepage"], None, None, {"width": 1280, "height": 800}),
    ]

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()

        for filename, path, username, password, viewport in shots:
            context = browser.new_context(viewport=viewport)
            page = context.new_page()
            if username:
                login(page, base_url, username, password)
            page.goto(f"{base_url}{path}")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(500)
            output = SCREENSHOT_DIR / filename
            page.screenshot(path=str(output), full_page=filename != "public-homepage.png")
            print(f"Saved {output}")
            context.close()

        browser.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Capture Roux landing page screenshots")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    args = parser.parse_args()
    setup_django()
    capture(args.base_url)


if __name__ == "__main__":
    main()
