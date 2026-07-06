from franchises.services import get_franchise_stripe_config


def site_context(request):
    organisation = getattr(request, "organisation", None)
    franchise = getattr(request, "franchise", None)
    site_settings = None
    nav_items = []
    pages = []

    if organisation:
        site_settings = getattr(organisation, "site_settings", None)
        nav_items = list(organisation.nav_items.filter(is_visible=True).select_related("page"))
        if not nav_items:
            pages = list(organisation.pages.filter(is_published=True, show_in_nav=True))

    stripe_config = get_franchise_stripe_config(franchise)

    return {
        "current_organisation": organisation,
        "current_franchise": franchise,
        "site_settings": site_settings,
        "nav_items": nav_items,
        "nav_pages": pages,
        "stripe_publishable_key": stripe_config["publishable_key"],
    }
