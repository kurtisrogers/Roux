# Roux developer documentation

Roux is an open-source Django SaaS platform for UK wraparound care providers — breakfast clubs, after-school clubs, and holiday programmes. It combines day-to-day operations, parent booking, CMS-driven websites, Ofsted compliance, and financial integrations in one extensible stack.

## Stack at a glance

| Area | Technology |
|------|------------|
| Backend | Django 5+, Django REST Framework, PostgreSQL (prod) / SQLite (dev) |
| Dashboard UI | Pico CSS, HTMX, Alpine.js, SortableJS page builder |
| Payments | Stripe Checkout for sessions; subscription billing for organisations |
| Accounting | Xero OAuth2 with automatic invoice sync on payment |
| Mobile | JWT-authenticated REST API at `/api/v1/` |
| Multi-tenant | Franchise partners with isolated databases and custom domains |

Source code: [github.com/kurtisrogers/Roux](https://github.com/kurtisrogers/Roux)

## What you can build

- **Club operations** — sessions, register, waitlist, vouchers, safeguarding
- **Programme planning** — Week A/B activities, closures, trips, run sheets
- **Parent experience** — branded CMS site, booking, payments, absence reporting
- **Compliance** — Ofsted incidents, EYFS ratio checks, CSV exports
- **Franchise networks** — isolated tenants, partner provisioning, custom domains

## Next steps

1. [Quick start](quick-start.md) — run locally in minutes
2. [Architecture](architecture.md) — understand the modular monolith
3. [Operations module](operations.md) — day-to-day club workflows
4. [AWS deployment](deployment.md) — ship to production
