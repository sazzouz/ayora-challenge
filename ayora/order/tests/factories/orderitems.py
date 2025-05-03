import factory
from core.tests.conftest import CleanModelFactory, fake


class OrderItemFactory(CleanModelFactory):
    item_id = factory.Faker("uuid4")

    class Meta:
        model = "order.OrderItem"

    order = factory.SubFactory(
        "order.tests.factories.OrderFactory",
    )
    quantity = fake("random_int", min=1, max=10)
