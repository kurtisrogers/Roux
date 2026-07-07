import os

os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "1")

pytest_plugins = [
    "e2e.steps.common_steps",
    "e2e.steps.programme_steps",
    "e2e.steps.operations_steps",
    "e2e.steps.parent_steps",
]
