# Extending Roux

| Goal | Where to start |
|------|----------------|
| New CMS block type | `cms/models.py` → `cms/block_forms.py` → `cms/block_renderer.py` |
| New user role | `accounts/models.py` → `accounts/decorators.py` |
| New payment integration | `billing/services/stripe_service.py` (follow existing Stripe pattern) |
| New API endpoint | `api/serializers.py` → `api/views.py` → `api/urls.py` |
| New email notification | `templates/emails/` → `notifications/services.py` |
| New dashboard feature | Add views in `dashboard/` or `operations/`, register in `dashboard/urls.py` |
| New programme block type | `programme/models.py` → `dashboard/programme_views.py` |
| New e2e scenario | `e2e/features/*.feature` → `e2e/steps/` → register in `e2e/test_bdd.py` |

## Contributing

Run `pre-commit run --all-files` before pushing. CI runs lint, unit tests, and Playwright e2e on every push to `main` and `skynet/**` branches.

Pull requests welcome at [github.com/kurtisrogers/Roux](https://github.com/kurtisrogers/Roux).
