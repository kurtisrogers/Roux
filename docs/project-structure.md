# Project structure

```
Roux/
├── accounts/          # Custom user model, roles, authentication
├── organisations/     # Multi-tenant orgs, sites, term dates
├── bookings/          # Children, sessions, bookings, attendance
├── cms/               # Site settings, pages, drag-and-drop page builder
├── billing/           # Stripe payments, subscriptions, refunds
├── finance/           # Xero integration
├── notifications/     # Email notifications and signals
├── ofsted/            # Incident logging, ratio checks, reports
├── operations/        # Register, waitlist, vouchers, safeguarding, analytics
├── programme/         # Activity catalogue, week packs, term programmes
├── api/               # REST API for mobile apps
├── franchises/        # Multi-franchise control plane and provisioning
├── dashboard/         # Staff/admin dashboard views
├── public_site/       # Customer-facing website
├── config/            # Django settings and root URLs
├── templates/         # Pico CSS templates (dashboard, public, emails)
├── static/            # CSS and JavaScript assets
├── e2e/               # Playwright BDD end-to-end tests
├── landing/           # Static marketing site (GitHub Pages)
├── docs/              # MkDocs developer documentation (this site)
└── infra/             # SST v3 AWS infrastructure
```
