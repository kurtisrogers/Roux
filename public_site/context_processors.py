def site_context(request):
    organisation = getattr(request, "organisation", None)
    site_settings = None
    nav_items = []
    pages = []

    if organisation:
        site_settings = getattr(organisation, "site_settings", None)
        nav_items = list(organisation.nav_items.filter(is_visible=True).select_related("page"))
        if not nav_items:
            pages = list(organisation.pages.filter(is_published=True, show_in_nav=True))

    return {
        "current_organisation": organisation,
        "site_settings": site_settings,
        "nav_items": nav_items,
        "nav_pages": pages,
        "stripe_publishable_key": __import__(
            "django.conf", fromlist=["settings"]
        ).settings.STRIPE_PUBLISHABLE_KEY,
    }
