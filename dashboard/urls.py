from django.urls import path

from dashboard import (
    franchise_application_views,
    franchise_views,
    ofsted_views,
    operations_views,
    views,
)

app_name = "dashboard"

urlpatterns = [
    path("", views.home, name="home"),
    # Franchises (platform / super admin)
    path("franchises/", franchise_views.franchise_list, name="franchise_list"),
    path("franchises/new/", franchise_views.franchise_create, name="franchise_create"),
    path("franchises/<int:pk>/", franchise_views.franchise_detail, name="franchise_detail"),
    path(
        "franchises/<int:pk>/integrations/",
        franchise_views.franchise_integrations,
        name="franchise_integrations",
    ),
    path(
        "franchise-applications/",
        franchise_application_views.application_list,
        name="franchise_application_list",
    ),
    path(
        "franchise-applications/<int:pk>/",
        franchise_application_views.application_detail,
        name="franchise_application_detail",
    ),
    # Children
    path("children/", views.child_list, name="child_list"),
    path("children/new/", views.child_create, name="child_create"),
    path("children/<int:pk>/edit/", views.child_edit, name="child_edit"),
    # Sessions
    path("sessions/", views.session_list, name="session_list"),
    path("sessions/new/", views.session_create, name="session_create"),
    path("sessions/<int:pk>/", views.session_detail, name="session_detail"),
    path("sessions/<int:pk>/register/", operations_views.session_register, name="session_register"),
    path(
        "sessions/<int:pk>/register/export/",
        operations_views.export_register,
        name="export_register",
    ),
    path(
        "sessions/<int:pk>/register/close/",
        operations_views.close_register_view,
        name="close_register",
    ),
    path(
        "sessions/<int:pk>/register/check-in-all/",
        operations_views.bulk_check_in_view,
        name="bulk_check_in",
    ),
    path("sessions/<int:pk>/walk-in/", operations_views.walk_in_booking, name="walk_in_booking"),
    path("sessions/bulk/", operations_views.bulk_sessions, name="bulk_sessions"),
    path("calendar/", operations_views.booking_calendar, name="booking_calendar"),
    path("recurring/", operations_views.recurring_list, name="recurring_list"),
    path("recurring/new/", operations_views.recurring_create, name="recurring_create"),
    path("waitlist/", operations_views.waitlist_list, name="waitlist_list"),
    path("rota/", operations_views.rota_list, name="rota_list"),
    path("rota/new/", operations_views.rota_create, name="rota_create"),
    path("visitors/", operations_views.visitor_list, name="visitor_list"),
    path("visitors/<int:pk>/sign-out/", operations_views.visitor_sign_out, name="visitor_sign_out"),
    path("medication/", operations_views.medication_list, name="medication_list"),
    path("compliance/", operations_views.staff_compliance_list, name="staff_compliance_list"),
    path(
        "compliance/<int:user_pk>/",
        operations_views.staff_compliance_edit,
        name="staff_compliance_edit",
    ),
    path("safeguarding/", operations_views.safeguarding_list, name="safeguarding_list"),
    path("safeguarding/new/", operations_views.safeguarding_create, name="safeguarding_create"),
    path(
        "safeguarding/from-incident/<int:incident_pk>/",
        operations_views.safeguarding_create,
        name="safeguarding_from_incident",
    ),
    path("subsidies/", operations_views.subsidy_list, name="subsidy_list"),
    path("vouchers/", operations_views.voucher_list, name="voucher_list"),
    path("vouchers/redeem/", operations_views.voucher_redeem, name="voucher_redeem"),
    path("payment-plans/", operations_views.payment_plan_list, name="payment_plan_list"),
    path("analytics/", operations_views.analytics_dashboard, name="analytics"),
    path(
        "children/<int:child_pk>/collectors/",
        operations_views.collector_list,
        name="collector_list",
    ),
    path(
        "bookings/<int:booking_pk>/no-show/",
        operations_views.mark_no_show_view,
        name="mark_no_show",
    ),
    path(
        "bookings/<int:booking_pk>/checkout/",
        operations_views.checkout_collector,
        name="checkout_collector",
    ),
    path(
        "finance/payments/<int:payment_pk>/refund/",
        operations_views.refund_payment_view,
        name="refund_payment",
    ),
    path(
        "franchises/<int:franchise_pk>/onboarding/",
        operations_views.franchise_onboarding,
        name="franchise_onboarding",
    ),
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
    path(
        "webhooks/stripe/<slug:franchise_slug>/",
        views.stripe_webhook,
        name="stripe_webhook_franchise",
    ),
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
