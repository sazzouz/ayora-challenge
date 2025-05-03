import factory
from core.tests.conftest import CleanModelFactory


class OrderPaymentFactory(CleanModelFactory):
    payment_info_id = factory.Faker("uuid4")

    class Meta:
        model = "order.OrderPayment"

    order = factory.SubFactory(
        "order.tests.factories.OrderFactory",
    )
