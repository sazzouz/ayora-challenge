from typing import TYPE_CHECKING

from django.db import models

from ..types.models import DjangoModelType

if TYPE_CHECKING:
    pass


class BaseManager(models.Manager[DjangoModelType]):
    pass


class BaseQuerySet(models.QuerySet[DjangoModelType]):
    pass
