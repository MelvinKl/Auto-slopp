"""Tests for HTTP requests worker."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from auto_slopp.workers.http_requests_worker import HttpRequestsWorker


class TestHttpRequestsWorker:
    """Test HttpRequestsWorker class."""

    def test_worker_initialization_defaults(self):
        """Test worker initialization with default parameters."""
        worker = HttpRequestsWorker()

        assert worker.method == "GET"
        assert worker.url is None
        assert worker.headers is None
        assert worker.data is None
        assert worker.json_data is None
        assert worker.timeout == 30.0

    def test_worker_initialization_custom_params(self):
        """Test worker initialization with custom parameters."""
        custom_headers = {"Authorization": "Bearer token"}
        custom_data = {"field": "value"}

        worker = HttpRequestsWorker(
            method="POST",
            url="https://api.example.com",
            headers=custom_headers,
            data=custom_data,
            timeout=60.0,
        )

        assert worker.method == "POST"
        assert worker.url == "https://api.example.com"
        assert worker.headers == custom_headers
        assert worker.data == custom_data
        assert worker.json_data is None
        assert worker.timeout == 60.0

    @patch("auto_slopp.workers.http_requests_worker.get")
    def test_get_request_success(self, mock_get):
        """Test successful GET request."""
        # Setup mock response
        mock_response = Mock()
        mock_response.success = True
        mock_response.status_code = 200
        mock_response.content = '{"message": "success"}'
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.error = None
        mock_get.return_value = mock_response

        worker = HttpRequestsWorker(url="https://api.example.com")
        result = worker.run(Path("/repo"), Path("/task"))

        assert result["success"] is True
        assert result["status_code"] == 200
        assert result["content"] == '{"message": "success"}'
        assert result["headers"] == {"Content-Type": "application/json"}
        assert result["url"] == "https://api.example.com"
        assert result["method"] == "GET"
        assert result["error"] is None

    @patch("auto_slopp.workers.http_requests_worker.post")
    def test_post_request_with_json(self, mock_post):
        """Test POST request with JSON data."""
        mock_response = Mock()
        mock_response.success = True
        mock_response.status_code = 201
        mock_response.content = '{"id": 1}'
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.error = None
        mock_post.return_value = mock_response

        json_data = {"name": "test"}
        worker = HttpRequestsWorker(
            method="POST", url="https://api.example.com", json_data=json_data
        )
        result = worker.run(Path("/repo"), Path("/task"))

        assert result["success"] is True
        assert result["status_code"] == 201
        mock_post.assert_called_once_with(
            "https://api.example.com", data=None, json=json_data, headers=None
        )

    @patch("auto_slopp.workers.http_requests_worker.put")
    def test_put_request_with_data(self, mock_put):
        """Test PUT request with form data."""
        mock_response = Mock()
        mock_response.success = True
        mock_response.status_code = 200
        mock_response.content = "Updated"
        mock_response.headers = {"Content-Type": "text/plain"}
        mock_response.error = None
        mock_put.return_value = mock_response

        data = {"field": "value"}
        worker = HttpRequestsWorker(
            method="PUT", url="https://api.example.com/1", data=data
        )
        result = worker.run(Path("/repo"), Path("/task"))

        assert result["success"] is True
        assert result["status_code"] == 200
        mock_put.assert_called_once_with(
            "https://api.example.com/1", data=data, json=None, headers=None
        )

    @patch("auto_slopp.workers.http_requests_worker.get")
    def test_http_error_response(self, mock_get):
        """Test handling of HTTP error responses."""
        mock_response = Mock()
        mock_response.success = False
        mock_response.status_code = 404
        mock_response.content = "Not Found"
        mock_response.headers = {}
        mock_response.error = None
        mock_get.return_value = mock_response

        worker = HttpRequestsWorker(url="https://api.example.com/notfound")
        result = worker.run(Path("/repo"), Path("/task"))

        assert result["success"] is False
        assert result["status_code"] == 404
        assert result["content"] == "Not Found"
        assert result["error"] is None

    @patch("auto_slopp.workers.http_requests_worker.get")
    def test_request_with_error(self, mock_get):
        """Test handling of request with error."""
        mock_response = Mock()
        mock_response.success = False
        mock_response.status_code = 0
        mock_response.content = ""
        mock_response.headers = {}
        mock_response.error = "Network error"
        mock_get.return_value = mock_response

        worker = HttpRequestsWorker(url="https://unreachable.example.com")
        result = worker.run(Path("/repo"), Path("/task"))

        assert result["success"] is False
        assert result["status_code"] == 0
        assert result["error"] == "Network error"

    def test_read_url_from_task_file(self, tmp_path):
        """Test reading URL from task file."""
        task_file = tmp_path / "task.txt"
        task_file.write_text("https://api.example.com/from-file", encoding="utf-8")

        worker = HttpRequestsWorker()
        # Don't mock get here since we want to test file reading part

        with patch("auto_slopp.workers.http_requests_worker.get") as mock_get:
            mock_response = Mock()
            mock_response.success = True
            mock_response.status_code = 200
            mock_response.content = "OK"
            mock_response.headers = {}
            mock_response.error = None
            mock_get.return_value = mock_response

            result = worker.run(Path("/repo"), task_file)

            assert result["success"] is True
            assert result["url"] == "https://api.example.com/from-file"
            mock_get.assert_called_once_with(
                "https://api.example.com/from-file", headers=None
            )

    def test_empty_task_file_error(self, tmp_path):
        """Test handling of empty task file."""
        task_file = tmp_path / "empty.txt"
        task_file.write_text("", encoding="utf-8")

        worker = HttpRequestsWorker()
        result = worker.run(Path("/repo"), task_file)

        assert result["success"] is False
        assert "Task file is empty" in result["error"]
        assert result["status_code"] == 0

    def test_no_url_error(self):
        """Test handling when no URL is provided."""
        # Create a task that doesn't exist
        non_existent_task = Path("/non/existent/task.txt")

        worker = HttpRequestsWorker()
        result = worker.run(Path("/repo"), non_existent_task)

        assert result["success"] is False
        assert "No URL provided" in result["error"]
        assert result["status_code"] == 0

    def test_task_file_read_error(self, tmp_path):
        """Test handling of task file read error."""
        # Create a directory where we expect a file
        task_dir = tmp_path / "not_a_file"
        task_dir.mkdir()

        worker = HttpRequestsWorker()
        result = worker.run(Path("/repo"), task_dir)

        assert result["success"] is False
        assert "No URL provided and could not read from task file" in result["error"]
        assert result["status_code"] == 0

    @patch("auto_slopp.workers.http_requests_worker.get")
    def test_unexpected_error_handling(self, mock_get):
        """Test handling of unexpected errors during request."""
        mock_get.side_effect = Exception("Unexpected error")

        worker = HttpRequestsWorker(url="https://api.example.com")
        result = worker.run(Path("/repo"), Path("/task"))

        assert result["success"] is False
        assert "Unexpected error during HTTP request" in result["error"]
        assert result["status_code"] == 0

    def test_custom_http_method(self):
        """Test using a custom HTTP method."""
        worker = HttpRequestsWorker(method="DELETE", url="https://api.example.com/1")

        # Since DELETE is not handled by specific methods, it will use the client directly
        with patch.object(worker.client, "_make_request") as mock_make_request:
            mock_response = Mock()
            mock_response.success = True
            mock_response.status_code = 204
            mock_response.content = ""
            mock_response.headers = {}
            mock_response.error = None
            mock_make_request.return_value = mock_response

            result = worker.run(Path("/repo"), Path("/task"))

            assert result["success"] is True
            assert result["method"] == "DELETE"

    def test_method_case_normalization(self):
        """Test that HTTP method is normalized to uppercase."""
        worker = HttpRequestsWorker(method="post")
        assert worker.method == "POST"

        worker = HttpRequestsWorker(method="get")
        assert worker.method == "GET"

        worker = HttpRequestsWorker(method="Put")
        assert worker.method == "PUT"
