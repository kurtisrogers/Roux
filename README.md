# Roux – UK Wraparound Care Platform

Roux is a Django SaaS platform for UK wraparound care providers (breakfast clubs, after-school clubs, holiday clubs). It competes with existing childcare management products by combining operations, parent booking, CMS-driven websites, and financial integrations in one extensible stack.

## Tech Stack

- **Backend:** Django 5+, Django REST Framework
- **Frontend:** [Pico CSS](https://picocss.com/), [HTMX](https://htmx.org/), [Alppine.js](https://alpinejs.dev/), [SortableJS](https://sortablejs.github.io/Sortable/)
- **Mobile API:** JWT authentication via djangorestframework-simplejwt
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
- **Drag-and-drop page builder** with SortableJS — reorder blocks visually
- **Visual block editors** for hero, rich text, CTA, FAQ, features, and more
- Block types: hero, rich text, features, CTA, FAQ, testimonials, session list, pricing, contact form
- Site settings (logo, colours, contact info, footer)
- Navigation management
- Parent registration and online session booking

### Email Notifications
- Booking confirmation emails to parents
- Payment received confirmations
- Check-in and check-out notifications
- Staff session reminders (`python manage.py send_session_reminders`)
- Console backend in dev; configure SMTP in production

### Mobile API (`/api/v1/`)
- JWT token auth: `POST /api/v1/auth/token/`
- `GET /api/v1/me/` — current user profile
- `GET /api/v1/sessions/` — list and upcoming sessions
- `GET/POST /api/v1/children/` — manage children
- `GET/POST /api/v1/bookings/` — create and view bookings
- `POST /api/v1/bookings/{id}/cancel/` — cancel a booking

### Ofsted & Compliance
- Incident logging (accidents, safeguarding, behaviour, medication)
- UK EYFS staff:child ratio checks per session
- Live ratio overview for today's sessions
- Monthly compliance reports
- CSV export for incidents and ratio checks
- Ofsted-notifiable incident flagging

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

### Email (production)

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your@email.com
EMAIL_HOST_PASSWORD=your-password
DEFAULT_FROM_EMAIL=noreply@yourclub.example
```

### Mobile API

```bash
# Obtain JWT token
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "parent1", "password": "parent123"}'

# Use token
curl http://localhost:8000/api/v1/sessions/upcoming/ \
  -H "Authorization: Bearer <access_token>"
```

## Project Structure

```
roux/
├── accounts/          # Custom user model, roles, auth
├── organisations/     # Multi-tenant orgs, sites, term dates
├── bookings/          # Children, sessions, bookings, attendance
├── cms/               # Site settings, pages, page builder blocks
├── billing/           # Stripe payments and subscriptions
├── finance/           # Xero integration
├── notifications/     # Email notifications and signals
├── ofsted/            # Incident logging, ratio checks, reports
├── api/               # REST API for mobile apps
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

- **New block types:** Add to `PageBlock.BlockType`, a form in `cms/block_forms.py`, and render in `cms/block_renderer.py`
- **New roles:** Extend `User.Role` and update `accounts/decorators.py`
- **New integrations:** Add apps under `billing/` or `finance/` following the service pattern
- **New API endpoints:** Add serializers and viewsets in `api/`
- **New notification types:** Add templates in `templates/emails/` and call from `notifications/services.py`

## Running Tests

```bash
# Install dev dependencies
pip install -r requirements.txt -r requirements-dev.txt

# Unit & integration tests
pytest

# With coverage
pytest --cov --cov-report=term-missing

# Playwright BDD e2e tests
playwright install chromium
DJANGO_ALLOW_ASYNC_UNSAFE=1 pytest e2e/ -m e2e --browser chromium
```

## Pre-commit

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

Hooks include: ruff lint/format, YAML/TOML checks, Django system check, and migration drift detection.

## GitHub Pages Landing Site

The marketing landing page lives in `landing/` and deploys automatically to GitHub Pages on push to `main`.

Enable GitHub Pages in repository settings: **Source → GitHub Actions**.

## AWS Deployment (SST)

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for full staging/production deployment instructions.

```bash
npm install
npm run deploy:staging      # staging environment
npm run deploy:production   # production (manual approval recommended)
```

## Licence

Proprietary – Roux
