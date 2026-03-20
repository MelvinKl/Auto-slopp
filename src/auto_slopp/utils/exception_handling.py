"""Utility functions for safe exception handling."""

import logging
from typing import Callable, Optional, TypeVar

T = TypeVar("T")
logger = logging.getLogger(__name__)


def safe_execute(
    func: Callable[..., T],
    *args,
    default: Optional[T] = None,
    log_errors: bool = True,
    **kwargs,
) -> Optional[T]:
    """
    Safely execute a function and return a default value on exception.

    Args:
        func: Function to execute
        *args: Arguments to pass to the function
        default: Value to return if exception occurs
        log_errors: Whether to log exceptions
        **kwargs: Keyword arguments to pass to the function

    Returns:
        Result of function execution or default value
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if log_errors:
            logger.error(f"Error executing {func.__name__}: {str(e)}")
        return default


def safe_execute_with_logging(
    func: Callable[..., T],
    *args,
    error_message: str = "An error occurred",
    log_errors: bool = True,
    **kwargs,
) -> Optional[T]:
    """
    Safely execute a function with custom error message.

    Args:
        func: Function to execute
        *args: Arguments to pass to the function
        error_message: Custom error message to log
        log_errors: Whether to log exceptions
        **kwargs: Keyword arguments to pass to the function

    Returns:
        Result of function execution or None
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if log_errors:
            logger.error(f"{error_message}: {str(e)}")
        return None
