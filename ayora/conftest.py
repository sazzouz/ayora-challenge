pytest_plugins = [
    "pytest_django.fixtures",
    "core.tests.fixtures",
    "celery.contrib.pytest",
    "order.tests.fixtures",
]
