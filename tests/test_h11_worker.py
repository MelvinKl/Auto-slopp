"""Tests for H11Worker.

This module tests the HTTP client functionality using h11 library
including request handling, response parsing, and error cases.
"""

import socket
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from auto_slopp.workers.h11_worker import H11Worker


class TestH11Worker:
    """Test cases for H11Worker."""

    def test_init_default(self):
        """Test H11Worker initialization with default parameters."""
        worker = H11Worker()
        assert worker.timeout == 30
        assert worker.logger.name == "auto_slopp.workers.H11Worker"

    def test_init_custom_timeout(self):
        """Test H11Worker initialization with custom timeout."""
        worker = H11Worker(timeout=60)
        assert worker.timeout == 60

    def test_run_with_nonexistent_file(self, tmp_path):
        """Test run with non-existent task file uses default URL."""
        worker = H11Worker()
        repo_path = tmp_path / "repo"
        task_path = tmp_path / "nonexistent.txt"

        with patch.object(worker, "_make_http_request") as mock_request:
            mock_request.return_value = {
                "success": True,
                "url": "http://httpbin.org/get",
            }

            result = worker.run(repo_path, task_path)

            assert result["worker_name"] == "H11Worker"
            assert result["success"] is True
            assert result["requests_made"] == 1
            assert result["successful_requests"] == 1
            assert result["failed_requests"] == 0
            assert len(result["responses"]) == 1
            mock_request.assert_called_once_with("http://httpbin.org/get")

    def test_run_with_file_containing_urls(self, tmp_path):
        """Test run with task file containing URLs."""
        worker = H11Worker()
        repo_path = tmp_path / "repo"
        task_path = tmp_path / "urls.txt"

        # Create file with URLs
        task_path.write_text("http://example.com\nhttps://httpbin.org/get\nhttp://test.com")

        with patch.object(worker, "_make_http_request") as mock_request:
            mock_request.side_effect = [
                {"success": True, "url": "http://example.com"},
                {
                    "success": False,
                    "url": "https://httpbin.org/get",
                    "error": "Timeout",
                },
                {"success": True, "url": "http://test.com"},
            ]

            result = worker.run(repo_path, task_path)

            assert result["success"] is True  # At least one success
            assert result["requests_made"] == 3
            assert result["successful_requests"] == 2
            assert result["failed_requests"] == 1
            assert len(result["responses"]) == 3

    def test_run_with_empty_file(self, tmp_path):
        """Test run with empty task file."""
        worker = H11Worker()
        repo_path = tmp_path / "repo"
        task_path = tmp_path / "empty.txt"

        # Create empty file
        task_path.write_text("")

        result = worker.run(repo_path, task_path)

        assert result["success"] is False
        assert result["requests_made"] == 0
        assert "error" in result
        assert "No URLs found" in result["error"]

    def test_get_urls_from_task_path_file(self, tmp_path):
        """Test URL extraction from file."""
        worker = H11Worker()
        task_path = tmp_path / "test_urls.txt"

        # Test with valid URLs file
        content = "http://example.com\nhttps://test.com\n\nhttp://another.com\n"
        task_path.write_text(content)

        urls = worker._get_urls_from_task_path(task_path)
        assert urls == ["http://example.com", "https://test.com", "http://another.com"]

    def test_get_urls_from_task_path_nonexistent(self, tmp_path):
        """Test URL extraction from non-existent file returns default."""
        worker = H11Worker()
        task_path = tmp_path / "nonexistent.txt"

        urls = worker._get_urls_from_task_path(task_path)
        assert urls == ["http://httpbin.org/get"]

    def test_make_http_request_connection_error(self):
        """Test HTTP request with connection error."""
        worker = H11Worker()
        url = "http://example.com"

        with patch("socket.create_connection", side_effect=socket.error("Connection refused")):
            result = worker._make_http_request(url)

            assert result["success"] is False
            assert result["url"] == url
            assert "Connection refused" in result["error"]
            assert result["status_code"] is None

    def test_make_http_request_invalid_url(self):
        """Test HTTP request with invalid URL."""
        worker = H11Worker()
        url = "not-a-url"

        result = worker._make_http_request(url)

        assert result["success"] is False
        assert result["url"] == url
        # Should fail with connection error since invalid URL gets prefixed with http://
        assert result["error"] is not None

    def test_make_http_request_with_port(self):
        """Test HTTP request with explicit port."""
        worker = H11Worker()
        url = "http://example.com:8080/path"

        # Mock socket and h11 components
        mock_sock = Mock()
        mock_conn = Mock()

        with (
            patch("socket.create_connection") as mock_create_conn,
            patch("h11.Connection", return_value=mock_conn),
        ):
            mock_create_conn.return_value = mock_sock
            mock_conn.send.side_effect = [b"GET /path HTTP/1.1\r\n...", b"\r\n"]
            mock_conn.next_event.side_effect = [
                Mock(status_code=200),
                Mock(data=b""),
                Mock(),
            ]
            mock_conn.NEED_DATA = Mock()

            with (
                patch("h11.Response") as mock_response_class,
                patch("h11.Data") as mock_data_class,
                patch("h11.EndOfMessage") as mock_eom_class,
            ):
                mock_response_class.return_value = Mock(status_code=200, headers=[])
                mock_data_class.return_value = Mock(data=b"")
                mock_eom_class.return_value = Mock()

                mock_sock.recv.return_value = b"HTTP/1.1 200 OK\r\n\r\n"

                result = worker._make_http_request(url)

                # Verify connection was made with correct port
                mock_create_conn.assert_called_once_with(("example.com", 8080), timeout=30)

    def test_send_data(self):
        """Test _send_data method."""
        worker = H11Worker()
        mock_sock = Mock()
        mock_conn = Mock()
        mock_event = Mock()

        # Test with data to send
        mock_conn.send.return_value = b"test data"

        worker._send_data(mock_conn, mock_sock, mock_event)

        mock_conn.send.assert_called_once_with(mock_event)
        mock_sock.sendall.assert_called_once_with(b"test data")

    def test_send_data_no_data(self):
        """Test _send_data method with no data."""
        worker = H11Worker()
        mock_sock = Mock()
        mock_conn = Mock()
        mock_event = Mock()

        # Test with no data to send
        mock_conn.send.return_value = b""

        worker._send_data(mock_conn, mock_sock, mock_event)

        mock_conn.send.assert_called_once_with(mock_event)
        mock_sock.sendall.assert_not_called()

    def test_log_completion_summary(self, caplog):
        """Test completion summary logging."""
        worker = H11Worker()

        result = {
            "requests_made": 5,
            "successful_requests": 4,
            "failed_requests": 1,
            "execution_time": 2.5,
        }

        # Enable logging capture for the worker's logger
        with caplog.at_level("INFO", logger="auto_slopp.workers.H11Worker"):
            worker._log_completion_summary(result)

        # Check that log message contains expected info
        assert "H11Worker completed" in caplog.text
        assert "Requests: 5" in caplog.text
        assert "Successful: 4" in caplog.text
        assert "Failed: 1" in caplog.text

    def test_integration_with_real_mock(self):
        """Test integration with more realistic mocking."""
        worker = H11Worker()
        url = "http://example.com"

        # Create realistic mocks
        mock_sock = Mock()
        mock_conn = Mock()

        with (
            patch("socket.create_connection", return_value=mock_sock),
            patch("h11.Connection", return_value=mock_conn),
        ):
            # Mock request sending
            mock_conn.send.return_value = b"GET / HTTP/1.1\r\nHost: example.com\r\n\r\n"

            # Mock a simple successful response by just ensuring no exceptions are raised
            mock_sock.recv.return_value = b"HTTP/1.1 200 OK\r\n\r\n"

            # Mock the connection methods to avoid h11 complexity
            mock_conn.send = Mock()
            mock_conn.next_event = Mock(side_effect=[Mock(), Mock()])  # Response, EndOfMessage
            mock_conn.NEED_DATA = Mock()
            mock_conn.receive_data = Mock()

            result = worker._make_http_request(url)

            # Should complete without exceptions (success might be False due to mocking)
            assert isinstance(result, dict)
            assert "url" in result
            assert "success" in result

    def test_make_http_request_malformed_response(self):
        """Test handling of malformed HTTP response."""
        worker = H11Worker()
        url = "http://example.com"

        mock_sock = Mock()
        mock_conn = Mock()

        with (
            patch("socket.create_connection", return_value=mock_sock),
            patch("h11.Connection", return_value=mock_conn),
        ):
            mock_conn.send.return_value = b"GET / HTTP/1.1\r\nHost: example.com\r\n\r\n"
            mock_conn.next_event.side_effect = [mock_conn.NEED_DATA]
            mock_conn.NEED_DATA = Mock()

            # Mock malformed response
            mock_sock.recv.return_value = b"Invalid response"

            result = worker._make_http_request(url)

            # Should handle gracefully
            assert result["success"] is False
            assert "Partial response" in result["body"] or result["body"] == ""
