# CI/CD

GitHub Actions workflows in `.github/workflows/`:

| Workflow | Trigger | Action |
|----------|---------|--------|
| `ci.yml` | Push / pull request | Pre-commit, unit tests with coverage, Playwright BDD e2e (Chromium) |
| `pages.yml` | Push to `main` | Build MkDocs + deploy marketing site to GitHub Pages |
| `deploy-sst.yml` | Push to `main` / manual | Deploy Django app to AWS via SST v3 |

Required GitHub secrets for deployment: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `DJANGO_SECRET_KEY`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `XERO_CLIENT_SECRET`.

## Local documentation build

```bash
pip install -r requirements-docs.txt
mkdocs serve
```

Open `http://127.0.0.1:8000` for live-reload preview of this documentation site.
