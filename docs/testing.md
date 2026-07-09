# Testing

## Unit & integration tests

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest
pytest --cov --cov-report=term-missing
```

## Playwright BDD e2e tests

End-to-end scenarios use pytest-bdd and Playwright against a live Django server:

```bash
playwright install chromium
DJANGO_ALLOW_ASYNC_UNSAFE=1 pytest e2e/ -m e2e --browser chromium
```

Feature files live in `e2e/features/` with shared step definitions in `e2e/steps/`. Scenarios cover auth, dashboard, public site, franchise flows, operations, programme planner, and parent booking journeys.

## Pre-commit hooks

```bash
pre-commit install
pre-commit run --all-files
```

Hooks: trailing whitespace, YAML/TOML/JSON checks, ruff lint + format, Django system check, migration drift detection.
