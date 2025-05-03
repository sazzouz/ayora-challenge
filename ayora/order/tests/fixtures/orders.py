from collections.abc import Callable

import pytest
from order.models import Order
from typeguard import typechecked

from ..generators import generate_orders as _generate_orders


@pytest.fixture
@typechecked
def generate_orders(db) -> Callable[[int | None, bool | None], list[Order]]:
    return _generate_orders
