from typing import TYPE_CHECKING

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_fsm import FSMField, transition

from ...constants import (
    ORDER__ACCEPTED_SOURCE_STATES,
    ORDER__REJECTED_SOURCE_STATES,
)
from ...enums import OrderStatus

if TYPE_CHECKING:
    from ...models import Order as OrderModelType


class OrderFK(models.Model):
    """Order foreign key mixin."""

    order: models.ForeignKey["OrderModelType"] = models.ForeignKey(
        to="order.Order",
        related_name="%(class)ss",
        on_delete=models.CASCADE,
        verbose_name=_("Order"),
        help_text=_("Order linked to object."),
    )

    class Meta:
        abstract = True


class OrderFSM(models.Model):
    """Order finite state machine (FSM) mixin."""

    status: FSMField = FSMField(
        max_length=24,
        choices=OrderStatus,
        default=OrderStatus.PLACED,
        verbose_name=_("Order Status"),
        help_text=_("Status of the order"),
    )
    accepted_at: models.DateTimeField = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Accepted At"),
        help_text=_("Date and time the order was accepted."),
    )
    rejected_at: models.DateTimeField = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Rejected At"),
        help_text=_("Date and time the order was rejected."),
    )

    class Meta:
        abstract = True

    # `ACCEPTED`

    def can_mark_as_accepted(self: "OrderModelType") -> bool:
        """Check if an order can be marked as accepted."""

        # check if the order is in a state to be marked as accepted
        if self.status not in ORDER__ACCEPTED_SOURCE_STATES:
            return False

        return True

    @transition(
        field=status,
        source=ORDER__ACCEPTED_SOURCE_STATES,
        target=OrderStatus.ACCEPTED,
        conditions=[can_mark_as_accepted],
    )
    def mark_as_accepted(self: "OrderModelType") -> None:
        """Mark an order as accepted."""

        # avoid circular import
        from ...services import order__update

        # update the order
        order__update(instance=self, updates={"accepted_at": timezone.now()})

    # `REJECTED`

    def can_mark_as_rejected(self: "OrderModelType") -> bool:
        """Check if an order can be marked as rejected."""

        # check if the order is in a state to be marked as rejected
        if self.status not in ORDER__REJECTED_SOURCE_STATES:
            return False

        return True

    @transition(
        field=status,
        source=ORDER__REJECTED_SOURCE_STATES,
        target=OrderStatus.REJECTED,
        conditions=[can_mark_as_rejected],
    )
    def mark_as_rejected(self: "OrderModelType") -> None:
        """Mark an order as rejected."""

        # avoid circular import
        from ...services import order__update

        # update the order
        order__update(instance=self, updates={"rejected_at": timezone.now()})
