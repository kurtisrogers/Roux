# Deployment Guide

Roux deploys to **AWS** using [SST v3](https://sst.dev/) with separate **staging** and **production** stages.

> SST targets AWS natively. For Azure, use Container Apps / App Service with equivalent Bicep or Terraform — the Docker image in this repo is cloud-agnostic.

## Architecture (per stage)

| Component | Staging | Production |
|-----------|---------|------------|
| Compute | ECS Fargate (1 task) | ECS Fargate (2–6 tasks) |
| Database | Aurora Serverless v2 (0.5–1 ACU) | Aurora Serverless v2 (0.5–4 ACU) |
| Static files | S3 + CloudFront | S3 + CloudFront |
| Uploads | S3 bucket | S3 bucket |
| Region | eu-west-2 (London) | eu-west-2 (London) |
| Domain | staging.roux.care | app.roux.care |

## Prerequisites

- AWS account with credentials configured
- Node.js 20+
- Docker (for image builds)
- Domain DNS pointed to SST load balancer (after first deploy)

## First-time setup

```bash
npm install

# Set secrets per stage
npx sst secret set SecretKey "<django-secret>" --stage staging
npx sst secret set StripeSecretKey "sk_test_..." --stage staging
npx sst secret set StripeWebhookSecret "whsec_..." --stage staging
npx sst secret set XeroClientSecret "..." --stage staging

# Deploy staging
npm run deploy:staging
```

Repeat with `--stage production` for production secrets and deploy.

## GitHub Actions

| Workflow | Trigger | Action |
|----------|---------|--------|
| `ci.yml` | Push / PR | Pre-commit, pytest, Playwright BDD |
| `pages.yml` | Push to `main` | Deploy `landing/` to GitHub Pages |
| `deploy-sst.yml` | Push to `main` | Deploy SST staging |
| `deploy-sst.yml` | Manual dispatch | Deploy staging or production |

### Required GitHub secrets

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `DJANGO_SECRET_KEY`
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `XERO_CLIENT_SECRET`

### GitHub Environments

Create `staging` and `production` environments in GitHub with appropriate protection rules for production.

## Local Docker

```bash
docker build -t roux .
docker run -p 8000:8000 -e SECRET_KEY=dev -e DEBUG=True roux
```

## Post-deploy

1. Run migrations: `npx sst shell --stage staging -- python manage.py migrate`
2. Seed demo data (staging only): `npx sst shell --stage staging -- python manage.py seed_demo`
3. Configure Stripe webhook URL: `https://<domain>/dashboard/webhooks/stripe/`
4. Configure Xero redirect: `https://<domain>/dashboard/finance/xero/callback/`
