from collections.abc import Callable

import pytest
from typeguard import typechecked

from order.models import OrderPayment

from ..generators import generate_order_payments as _generate_order_payments


@pytest.fixture
@typechecked
def generate_order_payments(
    db,
) -> Callable[[int | None, bool | None], list[OrderPayment]]:
    return _generate_order_payments
