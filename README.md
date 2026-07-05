# Roux – UK Wraparound Care Platform

Roux is a Django SaaS platform for UK wraparound care providers (breakfast clubs, after-school clubs, holiday clubs). It competes with existing childcare management products by combining operations, parent booking, CMS-driven websites, and financial integrations in one extensible stack.

## Tech Stack

- **Backend:** Django 5+
- **Frontend:** [Pico CSS](https://picocss.com/), [HTMX](https://htmx.org/), [Alpine.js](https://alpinejs.dev/)
- **Payments:** Stripe (parent session payments + org subscriptions)
- **Accounting:** Xero (invoice sync)
- **Database:** SQLite (dev) / PostgreSQL (production)

## Features (MVP)

### Operations Dashboard
- Role-based access: Super Admin, Org Admin, Site Manager, Staff, Finance, Parent
- Session and session-type management
- Child profiles with medical/allergy notes and emergency contacts
- Booking management with check-in/check-out (HTMX)
- Multi-site support per organisation
- UK term date tracking

### Customer Website (CMS)
- Pages edited entirely from the dashboard
- Block-based page builder (hero, rich text, features, CTA, FAQ, testimonials, session list, pricing, contact form)
- Site settings (logo, colours, contact info, footer)
- Navigation management
- Parent registration and online session booking

### Integrations
- **Stripe:** Checkout for session payments; subscription billing for organisations; webhook handling
- **Xero:** OAuth2 connect; automatic invoice creation on successful payments

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Run migrations
python manage.py migrate

# Seed demo data
python manage.py seed_demo

# Start server
python manage.py runserver
```

Visit http://localhost:8000 for the public site and http://localhost:8000/dashboard/ for the admin dashboard.

### Demo Credentials

| Role   | Username | Password   |
|--------|----------|------------|
| Admin  | admin    | admin123   |
| Staff  | staff1   | staff123   |
| Parent | parent1  | parent123  |

## Configuration

### Stripe

1. Create a [Stripe account](https://dashboard.stripe.com/register)
2. Add your test keys to `.env`:
   ```
   STRIPE_PUBLISHABLE_KEY=pk_test_...
   STRIPE_SECRET_KEY=sk_test_...
   STRIPE_WEBHOOK_SECRET=whsec_...
   ```
3. Forward webhooks locally: `stripe listen --forward-to localhost:8000/dashboard/webhooks/stripe/`

### Xero

1. Create an app at [Xero Developer](https://developer.xero.com/app/manage)
2. Set redirect URI to `http://localhost:8000/dashboard/finance/xero/callback/`
3. Add credentials to `.env`

## Project Structure

```
roux/
├── accounts/          # Custom user model, roles, auth
├── organisations/     # Multi-tenant orgs, sites, term dates
├── bookings/          # Children, sessions, bookings, attendance
├── cms/               # Site settings, pages, page builder blocks
├── billing/           # Stripe payments and subscriptions
├── finance/           # Xero integration
├── dashboard/         # Staff/admin dashboard views
├── public_site/       # Customer-facing website
├── config/            # Django settings and URLs
├── templates/         # Pico CSS templates
└── static/            # CSS and JS
```

## User Roles

| Role              | Access                                              |
|-------------------|-----------------------------------------------------|
| Super Admin       | All organisations (platform operator)               |
| Organisation Admin| Full org management, CMS, billing, users            |
| Site Manager      | Sessions, children, bookings, CMS                   |
| Staff             | Session management, check-in/out                    |
| Finance           | Billing, Xero, payment reports                      |
| Parent            | Public site, child profiles, bookings               |

## Extending Roux

The app is designed for extension:

- **New block types:** Add to `PageBlock.BlockType` and implement in `cms/block_renderer.py`
- **New roles:** Extend `User.Role` and update `accounts/decorators.py`
- **New integrations:** Add apps under `billing/` or `finance/` following the service pattern
- **API layer:** Add Django REST Framework when mobile apps are needed

## Running Tests

```bash
python manage.py test
```

## Licence

Proprietary – Roux
