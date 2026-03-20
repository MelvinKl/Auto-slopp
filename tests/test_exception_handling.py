"""Tests for exception handling utilities."""

from unittest.mock import patch

from auto_slopp.utils.exception_handling import safe_execute, safe_execute_with_logging


class TestSafeExecute:
    """Tests for safe_execute function."""

    def test_successful_execution(self):
        """Test successful function execution returns result."""

        def add(a, b):
            return a + b

        result = safe_execute(add, 1, 2)
        assert result == 3

    def test_exception_returns_default(self):
        """Test exception returns default value."""

        def failing_func():
            raise ValueError("Test error")

        result = safe_execute(failing_func, default="default_value")
        assert result == "default_value"

    def test_exception_no_default(self):
        """Test exception with no default returns None."""

        def failing_func():
            raise ValueError("Test error")

        result = safe_execute(failing_func)
        assert result is None

    def test_exception_logging_enabled(self):
        """Test that exceptions are logged when log_errors=True."""

        def failing_func():
            raise ValueError("Test error")

        with patch("auto_slopp.utils.exception_handling.logger") as mock_logger:
            result = safe_execute(failing_func, log_errors=True)
            assert result is None
            mock_logger.error.assert_called_once()
            assert "failing_func" in mock_logger.error.call_args[0][0]

    def test_exception_logging_disabled(self):
        """Test that exceptions are not logged when log_errors=False."""

        def failing_func():
            raise ValueError("Test error")

        with patch("auto_slopp.utils.exception_handling.logger") as mock_logger:
            result = safe_execute(failing_func, log_errors=False)
            assert result is None
            mock_logger.error.assert_not_called()

    def test_with_args_and_kwargs(self):
        """Test function with args and kwargs."""

        def func(a, b, key="default"):
            return f"{a}-{b}-{key}"

        result = safe_execute(func, 1, 2, key="custom")
        assert result == "1-2-custom"


class TestSafeExecuteWithLogging:
    """Tests for safe_execute_with_logging function."""

    def test_successful_execution(self):
        """Test successful function execution returns result."""

        def add(a, b):
            return a + b

        result = safe_execute_with_logging(add, 1, 2)
        assert result == 3

    def test_exception_returns_none(self):
        """Test exception returns None."""

        def failing_func():
            raise ValueError("Test error")

        result = safe_execute_with_logging(failing_func)
        assert result is None

    def test_exception_with_custom_message(self):
        """Test exception with custom error message."""

        def failing_func():
            raise ValueError("Test error")

        with patch("auto_slopp.utils.exception_handling.logger") as mock_logger:
            result = safe_execute_with_logging(failing_func, error_message="Custom error")
            assert result is None
            mock_logger.error.assert_called_once()
            assert "Custom error" in mock_logger.error.call_args[0][0]

    def test_exception_no_logging(self):
        """Test exception with logging disabled."""

        def failing_func():
            raise ValueError("Test error")

        with patch("auto_slopp.utils.exception_handling.logger") as mock_logger:
            result = safe_execute_with_logging(failing_func, log_errors=False)
            assert result is None
            mock_logger.error.assert_not_called()
