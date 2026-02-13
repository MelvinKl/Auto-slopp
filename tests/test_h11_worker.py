"""Tests for H11Worker."""

import logging
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from auto_slopp.workers.h11_worker import H11Worker


class TestH11Worker:
    """Test cases for H11Worker."""

    def test_worker_initialization(self):
        """Test H11Worker initialization with default timeout."""
        worker = H11Worker()
        assert worker.timeout == 30
        assert worker.logger is not None

    def test_worker_initialization_custom_timeout(self):
        """Test H11Worker initialization with custom timeout."""
        worker = H11Worker(timeout=60)
        assert worker.timeout == 60

    def test_parse_url_https(self):
        """Test URL parsing for HTTPS URLs."""
        worker = H11Worker()
        result = worker._parse_url("https://example.com/path")
        assert result == ("example.com", 443, "path", True)

    def test_parse_url_http(self):
        """Test URL parsing for HTTP URLs."""
        worker = H11Worker()
        result = worker._parse_url("http://example.com/path")
        assert result == ("example.com", 80, "path", False)

    def test_parse_url_with_port(self):
        """Test URL parsing with custom port."""
        worker = H11Worker()
        result = worker._parse_url("https://example.com:8443/path")
        assert result == ("example.com", 8443, "path", True)

    def test_parse_url_invalid(self):
        """Test URL parsing with invalid URL."""
        worker = H11Worker()
        result = worker._parse_url("not-a-url")
        assert result is None

    def test_parse_url_root_path(self):
        """Test URL parsing with root path."""
        worker = H11Worker()
        result = worker._parse_url("https://example.com")
        assert result == ("example.com", 443, "/", True)

    def test_get_urls_from_task_path_invalid(self):
        """Test URL extraction from non-existent path."""
        worker = H11Worker()
        result = worker._get_urls_from_task_path(Path("/nonexistent/path"))
        assert result == []

    @patch("auto_slopp.workers.h11_worker.Path.exists")
    def test_get_urls_from_file(self, mock_exists):
        """Test URL extraction from file."""
        mock_exists.return_value = True
        with patch("auto_slopp.workers.h11_worker.Path.is_file") as mock_is_file:
            mock_is_file.return_value = True
            with patch("auto_slopp.workers.h11_worker.Path.read_text") as mock_read:
                mock_read.return_value = "https://example.com\n# comment\nhttps://test.com"
                worker = H11Worker()
                result = worker._get_urls_from_task_path(Path("/test/file.txt"))
                assert result == ["https://example.com", "https://test.com"]

    def test_parse_url_from_path_direct_url(self):
        """Test URL parsing from direct URL string."""
        worker = H11Worker()
        result = worker._parse_url_from_path("https://example.com")
        assert result == "https://example.com"

    def test_parse_url_from_path_non_url(self):
        """Test URL parsing from non-URL string."""
        worker = H11Worker()
        result = worker._parse_url_from_path("/some/path")
        assert result is None

    @patch("auto_slopp.workers.h11_worker.socket.socket")
    def test_make_http_request_timeout(self, mock_socket):
        """Test HTTP request timeout handling."""
        import socket

        mock_sock_instance = MagicMock()
        mock_socket.return_value = mock_sock_instance
        mock_sock_instance.connect.side_effect = socket.timeout()

        worker = H11Worker(timeout=1)
        result = worker._make_http_request("https://example.com/")

        assert result["success"] is False
        assert result["error"] is not None

    @patch("auto_slopp.workers.h11_worker.socket.socket")
    def test_make_http_request_connection_error(self, mock_socket):
        """Test HTTP request connection error handling."""
        import socket

        mock_sock_instance = MagicMock()
        mock_socket.return_value = mock_sock_instance
        mock_sock_instance.connect.side_effect = socket.error("Connection refused")

        worker = H11Worker(timeout=1)
        result = worker._make_http_request("https://example.com/")

        assert result["success"] is False
        assert result["error"] is not None

    def test_run_with_invalid_path(self):
        """Test worker run with invalid task path."""
        worker = H11Worker()
        result = worker.run(Path("/repo"), Path("/nonexistent"))
        assert result["worker_name"] == "H11Worker"
        assert result["success"] is False
        assert "No URLs found" in result.get("error", "")
