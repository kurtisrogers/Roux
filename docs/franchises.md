# Franchises & multi-tenancy

Each franchise partner runs as an isolated wraparound business with its own database, branded website, Stripe account, and Xero connection. Hostname routing resolves the tenant.

## Provision a franchise (development)

```bash
python manage.py provision_franchise "Acme Care" \
  --slug acme \
  --hostname acme.localhost
```

Visit `http://acme.localhost:8000/` (add `acme.localhost` to `/etc/hosts` if needed).

## Partner application flow

Prospective partners apply at `/franchise/apply/` on the Django app. Super Admins review applications at **Dashboard → Franchise Applications** and progress them through **Pending → Under Review → Partner**. Approval provisions the isolated environment and emails login credentials.

## Production multi-database

SST sets `FRANCHISE_DATABASE_URL_TEMPLATE` so each partner gets a PostgreSQL database on the shared Aurora cluster. Point wildcard DNS at the load balancer:

- Staging: `*.staging.roux.care`
- Production: `*.roux.care`

## Operator model

Roux is software for operators who want to launch and run their own wraparound franchise — not a franchise sold by Roux. Deploy the platform, provision isolated tenants, and grow your network under your brand.
