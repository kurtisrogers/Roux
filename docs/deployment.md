# AWS deployment

Production deploys to **AWS eu-west-2 (London)** using [SST v3](https://sst.dev/).

## Architecture

| Component | Staging | Production |
|-----------|---------|------------|
| Compute | ECS Fargate (1 task) | ECS Fargate (2–6 tasks) |
| Database | Aurora Serverless v2 | Aurora Serverless v2 (scaled) |
| Static files | S3 + CloudFront | S3 + CloudFront |
| Domain | `staging.roux.care` | `app.roux.care` |

## First deploy

```bash
npm install
npx sst secret set SecretKey "<django-secret>" --stage staging
npx sst secret set StripeSecretKey "sk_test_..." --stage staging
npm run deploy:staging
```

## Post-deploy checklist

1. Run migrations: `npx sst shell --stage staging -- python manage.py migrate`
2. Seed demo data on staging: `npx sst shell --stage staging -- python manage.py seed_demo`
3. Configure Stripe webhook: `https://<domain>/dashboard/webhooks/stripe/`
4. Configure Xero redirect: `https://<domain>/dashboard/finance/xero/callback/`

## Docker (local)

```bash
docker build -t roux .
docker run -p 8000:8000 -e SECRET_KEY=dev -e DEBUG=True roux
```

## Multi-franchise databases

Each franchise partner gets an isolated PostgreSQL database on the shared Aurora cluster. SST sets `FRANCHISE_DATABASE_URL_TEMPLATE` with a `{db_name}` placeholder. Point wildcard DNS at the load balancer:

- Staging: `*.staging.roux.care`
- Production: `*.roux.care`

See the full deployment guide in the repository at `docs/DEPLOYMENT.md` for additional detail on secrets, environments, and Azure alternatives.
