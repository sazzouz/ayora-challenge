import time
from contextlib import contextmanager
from random import seed

import pytest
from django.core.exceptions import ValidationError
from factory import Faker
from factory.django import DjangoModelFactory
from factory.random import reseed_random
from rest_framework.reverse import reverse
from typeguard import typechecked

########################################################################################
# constants ############################################################################
########################################################################################


DEFAULT_SEED_VALUE = 0


########################################################################################
# utils ################################################################################
########################################################################################


@typechecked
def get_fake_instance() -> type["Faker"]:
    fake = Faker
    reseed_random(DEFAULT_SEED_VALUE)
    seed(DEFAULT_SEED_VALUE)
    return fake


fake = get_fake_instance()
faker = fake._get_faker()


def generate_rand_int(min_value: int = 1, max_value: int = 100) -> int:
    """Return a random integer between `min_value` and `max_value`."""

    return faker.pyint(min_value=min_value, max_value=max_value)


@typechecked
def get_url(name: str, kwargs: dict | None = None) -> str:
    """Resolve the URL for the given name."""

    if kwargs:
        return reverse(name, kwargs=kwargs)
    return reverse(name)


@typechecked
def get_url_uid(name: str, uid: str) -> str:
    """Resolve the URL for the given name and `uid`."""

    return get_url(name=name, kwargs={"uid": uid})


@typechecked
def assert_nested_validation_error_code(
    response_data: dict,
    error_type: str = "validation_error",
    expected_error_code: str = "",
):
    if "type" not in response_data or response_data["type"] != error_type:
        raise AssertionError("Response error type invalid.")

    errors = response_data.get("errors", [])
    for error in errors:
        if "code" in error and error["code"] == expected_error_code:
            return  # Found the expected error code, no assertion error

    raise AssertionError(f"Expected error code '{expected_error_code}' not found in the response data.")


def flaky_rerun_delay(*args):
    time.sleep(1)
    return True


@contextmanager
def assert_not_raises(exception: Exception):
    """Assert that the given exception is not raised."""

    try:
        yield
    except exception:
        raise pytest.fail(f"DID RAISE {exception}")


########################################################################################
# mixins ###############################################################################
########################################################################################


class BaseModelFactory(DjangoModelFactory):
    """Base class for all model factories."""

    class Meta:
        abstract = True


class CleanModelFactory(BaseModelFactory):
    """
    Ensures that created instances pass Django's `full_clean` checks.

    NOTE: adapted from https://github.com/jamescooke/factory_djoy/,
    see for known limitations.
    """

    class Meta:
        abstract = True

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """
        Call `full_clean` on any created instance before saving

        Returns:
            model_class

        Raises:
            RuntimeError: Raised when validation fails on built model instance.
        """

        # handle get or create
        get_or_create_fields = cls._meta.django_get_or_create
        if get_or_create_fields:
            try:
                obj = model_class._default_manager.get(**{field: kwargs[field] for field in get_or_create_fields})

                # handle soft-deleted models
                if hasattr(obj, "deleted_at"):
                    # if the object is soft-deleted, treat as if it doesn't exist
                    if obj.deleted_at is not None:
                        raise model_class.DoesNotExist

            except model_class.DoesNotExist:
                obj = model_class(*args, **kwargs)
        else:
            obj = model_class(*args, **kwargs)

        # attempt to validate the model instance
        try:
            obj.full_clean()
        except ValidationError as ve:
            message = f"Error building {model_class} with {cls.__name__}.\nBad values:\n"
            for field, value in ve.error_dict.items():
                if field == "__all__":
                    errors = [error for error in ve.error_dict.values()]
                    message += f"  __all__: {[errors]}\n" if len(errors) > 1 else f"  __all__: {errors[0]}\n"
                else:
                    message += f'  {field}: "{getattr(obj, field)}: {value}"\n'
            raise RuntimeError(message) from ve
        obj.save()

        return obj
