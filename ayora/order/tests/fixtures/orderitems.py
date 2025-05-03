from collections.abc import Callable

import pytest
from order.models import OrderItem
from typeguard import typechecked

from ..generators import generate_order_items as _generate_order_items


@pytest.fixture
@typechecked
def generate_order_items(
    db,
) -> Callable[[int | None, bool | None], list[OrderItem]]:
    return _generate_order_items
