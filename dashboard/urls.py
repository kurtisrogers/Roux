from django.urls import path

from dashboard import ofsted_views, views

app_name = "dashboard"

urlpatterns = [
    path("", views.home, name="home"),
    # Children
    path("children/", views.child_list, name="child_list"),
    path("children/new/", views.child_create, name="child_create"),
    path("children/<int:pk>/edit/", views.child_edit, name="child_edit"),
    # Sessions
    path("sessions/", views.session_list, name="session_list"),
    path("sessions/new/", views.session_create, name="session_create"),
    path("sessions/<int:pk>/", views.session_detail, name="session_detail"),
    path("session-types/", views.session_type_list, name="session_type_list"),
    path("session-types/new/", views.session_type_create, name="session_type_create"),
    # Bookings
    path("bookings/", views.booking_list, name="booking_list"),
    path("bookings/<int:booking_pk>/check-in/", views.check_in, name="check_in"),
    path("bookings/<int:booking_pk>/check-out/", views.check_out, name="check_out"),
    # CMS
    path("cms/pages/", views.page_list, name="page_list"),
    path("cms/pages/new/", views.page_create, name="page_create"),
    path("cms/pages/<int:pk>/", views.page_edit, name="page_edit"),
    path("cms/pages/<int:page_pk>/blocks/add/", views.block_add, name="block_add"),
    path("cms/blocks/<int:pk>/edit/", views.block_edit, name="block_edit"),
    path("cms/blocks/<int:pk>/delete/", views.block_delete, name="block_delete"),
    path("cms/pages/<int:page_pk>/blocks/reorder/", views.block_reorder, name="block_reorder"),
    path("cms/settings/", views.site_settings_edit, name="site_settings"),
    path("cms/contacts/", views.contact_list, name="contact_list"),
    # Users & sites
    path("users/", views.user_list, name="user_list"),
    path("users/new/", views.user_create, name="user_create"),
    path("sites/", views.site_list, name="site_list"),
    path("sites/new/", views.site_create, name="site_create"),
    # Billing
    path("billing/", views.billing, name="billing"),
    path("billing/subscribe/", views.billing_subscribe, name="billing_subscribe"),
    path("billing/success/", views.billing_success, name="billing_success"),
    path("webhooks/stripe/", views.stripe_webhook, name="stripe_webhook"),
    # Finance
    path("finance/", views.finance, name="finance"),
    path("finance/xero/connect/", views.xero_connect, name="xero_connect"),
    path("finance/xero/callback/", views.xero_callback, name="xero_callback"),
    path("finance/xero/disconnect/", views.xero_disconnect, name="xero_disconnect"),
    path(
        "finance/payments/<int:payment_pk>/sync/",
        views.sync_payment_to_xero,
        name="sync_payment_to_xero",
    ),
    # Ofsted & compliance
    path("ofsted/", ofsted_views.ofsted_dashboard, name="ofsted_dashboard"),
    path("ofsted/incidents/", ofsted_views.incident_list, name="incident_list"),
    path("ofsted/incidents/new/", ofsted_views.incident_create, name="incident_create"),
    path("ofsted/ratios/", ofsted_views.ratio_overview, name="ratio_overview"),
    path(
        "ofsted/sessions/<int:session_pk>/ratio-check/",
        ofsted_views.ratio_check_session,
        name="ratio_check_session",
    ),
    path("ofsted/reports/generate/", ofsted_views.generate_report, name="generate_report"),
    path("ofsted/export/incidents/", ofsted_views.export_incidents, name="export_incidents"),
    path("ofsted/export/ratios/", ofsted_views.export_ratios, name="export_ratios"),
]
