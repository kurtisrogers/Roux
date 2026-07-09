# Configuration

## Stripe

1. Create a [Stripe account](https://dashboard.stripe.com/register) and copy test keys into `.env`.
2. Forward webhooks locally:

```bash
stripe listen --forward-to localhost:8000/dashboard/webhooks/stripe/
```

3. Per-franchise webhooks: `POST /dashboard/webhooks/stripe/<franchise_slug>/`

## Xero

1. Create an app at [Xero Developer](https://developer.xero.com/app/manage).
2. Set redirect URI to `http://localhost:8000/dashboard/finance/xero/callback/` (or your production domain).
3. Connect from **Dashboard → Finance → Connect Xero**.

## Email

Development uses the console backend. For production:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your@email.com
EMAIL_HOST_PASSWORD=your-password
DEFAULT_FROM_EMAIL=noreply@yourclub.example
```

Notification types include booking confirmations, payment receipts, check-in/out alerts, absence reports, waitlist promotions, voucher redemptions, and DBS expiry reminders.
