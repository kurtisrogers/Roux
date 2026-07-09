# Quick start

Requires **Python 3.12+**. Clone the repository and install dependencies:

```bash
git clone https://github.com/kurtisrogers/Roux.git
cd Roux
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

## Local URLs

| URL | Purpose |
|-----|---------|
| `http://localhost:8000/` | Public homepage (CMS-driven per organisation) |
| `http://localhost:8000/dashboard/` | Staff operations dashboard |
| `http://localhost:8000/admin/` | Django admin |

## Pre-commit (recommended)

Install hooks before contributing:

```bash
pip install pre-commit && pre-commit install
```

See [Demo credentials](demo-credentials.md) for login details after seeding.
