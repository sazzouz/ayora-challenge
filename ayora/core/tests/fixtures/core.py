from collections.abc import Callable
from random import seed

import pytest
from django.core.cache import cache
from factory.random import reseed_random
from rest_framework.test import APIClient
from typeguard import typechecked

from core.tests.conftest import fake

from ..conftest import DEFAULT_SEED_VALUE
from ..conftest import generate_rand_int as _generate_rand_int

faker = fake._get_faker()


@pytest.fixture(autouse=True)
@typechecked
def clear_django_cache() -> None:
    """Clears the Django cache before each test."""

    cache.clear()


@pytest.fixture(autouse=True)
def set_seed() -> None:
    """Sets the seed for testing with randomness, providing reproducibility."""

    reseed_random(DEFAULT_SEED_VALUE)
    seed(DEFAULT_SEED_VALUE)


@pytest.fixture
@typechecked
def generate_rand_int() -> Callable[[int], int]:
    """Provides a function to generate a random integer."""

    return _generate_rand_int


@pytest.fixture
@typechecked
def api_client() -> APIClient:
    """Unauthenticated (anonymous) API client."""

    return APIClient()
