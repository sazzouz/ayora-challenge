from typing import Any


def custom_preprocessing_hook(endpoints: Any) -> Any:
    """Custom preprocessing hook for API schema generation."""

    # handle endpoints
    for path, path_regex, method, callback in endpoints:
        pass

    return endpoints


def custom_postprocessing_hook(result: Any, generator: Any, **kwargs: Any) -> Any:
    """Custom postprocessing hook for API schema generation."""

    return result
