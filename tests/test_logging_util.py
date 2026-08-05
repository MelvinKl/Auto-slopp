"""Tests for the logging utility module."""

import logging

from auto_slopp.utils.logging_util import add_file_handler, setup_file_handler


class TestSetupFileHandler:
    """Test cases for setup_file_handler."""

    def test_creates_log_directory(self, temp_dir):
        """Test that the log directory is created if it doesn't exist."""
        log_dir = temp_dir / "logs" / "nested"
        handler = setup_file_handler(log_dir=log_dir)
        try:
            assert log_dir.is_dir()
        finally:
            handler.close()

    def test_creates_log_file(self, temp_dir):
        """Test that the log file is created."""
        log_dir = temp_dir / "logs"
        handler = setup_file_handler(log_dir=log_dir)
        try:
            assert (log_dir / "auto_slopp.log").exists()
        finally:
            handler.close()

    def test_custom_filename(self, temp_dir):
        """Test custom log file name."""
        log_dir = temp_dir / "logs"
        handler = setup_file_handler(log_dir=log_dir, filename="custom.log")
        try:
            assert (log_dir / "custom.log").exists()
        finally:
            handler.close()

    def test_default_level_is_warning(self, temp_dir):
        """Test that the default log level is WARNING."""
        log_dir = temp_dir / "logs"
        handler = setup_file_handler(log_dir=log_dir)
        try:
            assert handler.level == logging.WARNING
        finally:
            handler.close()

    def test_custom_level(self, temp_dir):
        """Test setting a custom log level."""
        log_dir = temp_dir / "logs"
        handler = setup_file_handler(log_dir=log_dir, level=logging.DEBUG)
        try:
            assert handler.level == logging.DEBUG
        finally:
            handler.close()

    def test_rotating_file_handler_type(self, temp_dir):
        """Test that the returned handler is a RotatingFileHandler."""
        from logging.handlers import RotatingFileHandler

        log_dir = temp_dir / "logs"
        handler = setup_file_handler(log_dir=log_dir)
        try:
            assert isinstance(handler, RotatingFileHandler)
        finally:
            handler.close()

    def test_writes_warning_logs(self, temp_dir):
        """Test that WARNING level logs are written to the file."""
        log_dir = temp_dir / "logs"
        handler = setup_file_handler(log_dir=log_dir)
        try:
            logger = logging.getLogger(f"test_warning_{id(temp_dir)}")
            logger.addHandler(handler)
            logger.setLevel(logging.WARNING)
            logger.warning("Test warning message")

            log_file = log_dir / "auto_slopp.log"
            content = log_file.read_text()
            assert "Test warning message" in content
        finally:
            logger.removeHandler(handler)
            handler.close()

    def test_ignores_info_logs_by_default(self, temp_dir):
        """Test that INFO level logs are not written (default level is WARNING)."""
        log_dir = temp_dir / "logs"
        handler = setup_file_handler(log_dir=log_dir)
        try:
            logger = logging.getLogger(f"test_info_{id(temp_dir)}")
            logger.addHandler(handler)
            logger.setLevel(logging.DEBUG)
            logger.info("This should not appear")

            log_file = log_dir / "auto_slopp.log"
            content = log_file.read_text()
            assert "This should not appear" not in content
        finally:
            logger.removeHandler(handler)
            handler.close()


class TestAddFileHandler:
    """Test cases for add_file_handler."""

    def test_adds_handler_to_logger(self, temp_dir):
        """Test that the handler is added to the logger."""
        log_dir = temp_dir / "logs"
        logger = logging.getLogger(f"test_add_{id(temp_dir)}")
        try:
            handler = add_file_handler(logger=logger, log_dir=log_dir)
            assert handler in logger.handlers
        finally:
            logger.removeHandler(handler)

    def test_returns_handler(self, temp_dir):
        """Test that the handler is returned."""
        from logging.handlers import RotatingFileHandler

        log_dir = temp_dir / "logs"
        logger = logging.getLogger(f"test_return_{id(temp_dir)}")
        try:
            handler = add_file_handler(logger=logger, log_dir=log_dir)
            assert isinstance(handler, RotatingFileHandler)
        finally:
            logger.removeHandler(handler)

    def test_sets_handler_level(self, temp_dir):
        """Test that the handler level is set correctly."""
        log_dir = temp_dir / "logs"
        logger = logging.getLogger(f"test_level_{id(temp_dir)}")
        try:
            handler = add_file_handler(logger=logger, log_dir=log_dir, level=logging.ERROR)
            assert handler.level == logging.ERROR
        finally:
            logger.removeHandler(handler)

    def test_writes_error_and_critical_logs(self, temp_dir):
        """Test that ERROR and CRITICAL logs are written to the file."""
        log_dir = temp_dir / "logs"
        handler = setup_file_handler(log_dir=log_dir)
        try:
            logger = logging.getLogger(f"test_error_{id(temp_dir)}")
            logger.addHandler(handler)
            logger.setLevel(logging.DEBUG)
            logger.error("Test error message")
            logger.critical("Test critical message")

            log_file = log_dir / "auto_slopp.log"
            content = log_file.read_text()
            assert "Test error message" in content
            assert "Test critical message" in content
        finally:
            logger.removeHandler(handler)
            handler.close()

    def test_handler_configuration(self, temp_dir):
        """Test that the handler has correct maxBytes and backupCount."""
        log_dir = temp_dir / "logs"
        handler = setup_file_handler(
            log_dir=log_dir,
            max_bytes=5 * 1024 * 1024,
            backup_count=3,
        )
        try:
            assert handler.maxBytes == 5 * 1024 * 1024
            assert handler.backupCount == 3
        finally:
            handler.close()

    def test_handler_formatter(self, temp_dir):
        """Test that the handler has the correct formatter."""
        log_dir = temp_dir / "logs"
        handler = setup_file_handler(log_dir=log_dir)
        try:
            formatter = handler.formatter
            assert formatter is not None
            # Check that the format includes expected fields
            fmt = formatter._fmt
            assert "%(asctime)s" in fmt
            assert "%(name)s" in fmt
            assert "%(levelname)s" in fmt
            assert "%(message)s" in fmt
        finally:
            handler.close()

    def test_log_file_format(self, temp_dir):
        """Test that the log file content has the expected format."""
        log_dir = temp_dir / "logs"
        handler = setup_file_handler(log_dir=log_dir)
        try:
            logger = logging.getLogger(f"test_format_{id(temp_dir)}")
            logger.addHandler(handler)
            logger.setLevel(logging.WARNING)
            logger.warning("Format test message")

            log_file = log_dir / "auto_slopp.log"
            content = log_file.read_text().strip()
            # Log format: asctime - name - level - message
            parts = content.split(" - ", 3)
            assert len(parts) >= 4
            assert parts[1].startswith("test_format_")
            assert parts[2] == "WARNING"
            assert parts[3] == "Format test message"
        finally:
            logger.removeHandler(handler)
            handler.close()

    def test_add_file_handler_default_level(self, temp_dir):
        """Test that add_file_handler uses WARNING as default level."""
        log_dir = temp_dir / "logs"
        logger = logging.getLogger(f"test_default_level_{id(temp_dir)}")
        try:
            handler = add_file_handler(logger=logger, log_dir=log_dir)
            assert handler.level == logging.WARNING
        finally:
            logger.removeHandler(handler)

    def test_add_file_handler_custom_params(self, temp_dir):
        """Test add_file_handler with custom parameters."""
        log_dir = temp_dir / "logs"
        logger = logging.getLogger(f"test_custom_params_{id(temp_dir)}")
        try:
            handler = add_file_handler(
                logger=logger,
                log_dir=log_dir,
                filename="custom.log",
                max_bytes=2 * 1024 * 1024,
                backup_count=2,
                level=logging.ERROR,
            )
            assert handler.maxBytes == 2 * 1024 * 1024
            assert handler.backupCount == 2
            assert handler.level == logging.ERROR
            assert (log_dir / "custom.log").exists()
        finally:
            logger.removeHandler(handler)

    def test_handler_encoding_is_utf8(self, temp_dir):
        """Test that the handler uses utf-8 encoding."""
        log_dir = temp_dir / "logs"
        handler = setup_file_handler(log_dir=log_dir)
        try:
            assert handler.encoding == "utf-8"
        finally:
            handler.close()
