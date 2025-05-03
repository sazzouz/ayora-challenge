from typeguard import typechecked


@typechecked
def instance_but_not_subclass(*, object: object, klass: type) -> bool:
    """Return if an object is an instance of a class but not a subclass."""

    return type(object) is klass
