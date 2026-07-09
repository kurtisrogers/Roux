# Environment variables

Copy `.env.example` to `.env` and configure:

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | Yes (prod) | Django secret key |
| `DEBUG` | Dev only | Set `True` for local development |
| `ALLOWED_HOSTS` | Prod | Comma-separated hostnames |
| `DATABASE_URL` | Prod | PostgreSQL connection string (SQLite used if unset in dev) |
| `STRIPE_PUBLISHABLE_KEY` | For payments | Stripe publishable key |
| `STRIPE_SECRET_KEY` | For payments | Stripe secret key |
| `STRIPE_WEBHOOK_SECRET` | For payments | Stripe webhook signing secret |
| `XERO_CLIENT_ID` | For Xero | Xero OAuth app client ID |
| `XERO_CLIENT_SECRET` | For Xero | Xero OAuth app client secret |
| `XERO_REDIRECT_URI` | For Xero | OAuth callback URL |
| `EMAIL_BACKEND` | Prod | SMTP backend for production email |
| `DEFAULT_FROM_EMAIL` | Prod | Sender address for notifications |
| `PLATFORM_ADMIN_EMAIL` | Optional | Receives alerts for new franchise applications |
| `FRANCHISE_DATABASE_URL_TEMPLATE` | Prod multi-tenant | PostgreSQL URL template with `{db_name}` placeholder |
| `FRANCHISE_BASE_DOMAIN` | Prod multi-tenant | Base domain for partner hostnames (e.g. `roux.care`) |
