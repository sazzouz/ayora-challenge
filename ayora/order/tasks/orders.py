from typing import Any

from celery import Task
from config.celery import app
from typeguard import typechecked


@typechecked
class RejectStaleOrdersTask(Task):
    """Task to reject stale orders that were never accepted."""

    def run(self, *args: Any, **kwargs: Any) -> int:
        # avoid circular import
        from ..services import order__handle__stale_orders

        # handle stale orders (if they exist)
        # NOTE: utilises a service to be decoupled from runtime-specific task implementation (i.e. Celery)
        # making it simple to run this inside of serverless environment or elsewhere, and more unit-testable
        # TODO: migrate task logic to instead make a `POST` request to a dedicated endpoint to have complete decoupling
        count = order__handle__stale_orders()

        return count


RejectStaleOrdersTask = app.register_task(RejectStaleOrdersTask())
