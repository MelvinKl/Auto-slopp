"""Tests for HTTP requests utility."""

import json
from unittest.mock import Mock, patch

import httpx
import pytest
from httpx._types import RequestData

from auto_slopp.utils.http_requests import (
    HttpClient,
    HttpResponse,
    get,
    get_default_client,
    post,
    put,
)


class TestHttpResponse:
    """Test HttpResponse model."""

    def test_http_response_creation(self):
        """Test creating an HTTP response."""
        response = HttpResponse(
            status_code=200,
            content="OK",
            headers={"Content-Type": "text/plain"},
            success=True,
        )

        assert response.status_code == 200
        assert response.content == "OK"
        assert response.headers == {"Content-Type": "text/plain"}
        assert response.success is True
        assert response.error is None

    def test_http_response_with_error(self):
        """Test creating an HTTP response with error."""
        response = HttpResponse(status_code=0, content="", headers={}, success=False, error="Network error")

        assert response.status_code == 0
        assert response.content == ""
        assert response.success is False
        assert response.error == "Network error"


class TestHttpClient:
    """Test HttpClient class."""

    def test_client_initialization(self):
        """Test client initialization with default parameters."""
        client = HttpClient()

        assert client.timeout == 30.0
        assert client.default_headers == {}
        assert client.follow_redirects is True

    def test_client_initialization_with_custom_params(self):
        """Test client initialization with custom parameters."""
        custom_headers = {"User-Agent": "test-agent"}
        client = HttpClient(timeout=60.0, headers=custom_headers, follow_redirects=False)

        assert client.timeout == 60.0
        assert client.default_headers == custom_headers
        assert client.follow_redirects is False

    @patch("auto_slopp.utils.http_requests.httpx.Client")
    def test_get_request_success(self, mock_client_class):
        """Test successful GET request."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "Success!"
        mock_response.headers = {"Content-Type": "text/plain"}

        mock_client = Mock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        # Make request
        client = HttpClient()
        response = client.get("https://example.com")

        # Verify response
        assert response.status_code == 200
        assert response.content == "Success!"
        assert response.headers == {"Content-Type": "text/plain"}
        assert response.success is True

        # Verify mock calls
        mock_client.request.assert_called_once_with(
            method="GET", url="https://example.com", data=None, json=None, headers={}
        )

    @patch("auto_slopp.utils.http_requests.httpx.Client")
    def test_post_request_with_json(self, mock_client_class):
        """Test POST request with JSON data."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.text = '{"id": 1}'
        mock_response.headers = {"Content-Type": "application/json"}

        mock_client = Mock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        client = HttpClient()
        json_data = {"name": "test"}
        response = client.post("https://api.example.com", json=json_data)

        assert response.status_code == 201
        assert response.success is True
        mock_client.request.assert_called_once_with(
            method="POST",
            url="https://api.example.com",
            data=None,
            json=json_data,
            headers={},
        )

    @patch("auto_slopp.utils.http_requests.httpx.Client")
    def test_put_request_with_data(self, mock_client_class):
        """Test PUT request with form data."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "Updated"
        mock_response.headers = {"Content-Type": "text/plain"}

        mock_client = Mock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        client = HttpClient()
        form_data = "field=value"
        response = client.put("https://api.example.com/1", data=form_data)

        assert response.status_code == 200
        assert response.success is True
        mock_client.request.assert_called_once_with(
            method="PUT",
            url="https://api.example.com/1",
            data=form_data,
            json=None,
            headers={},
        )

    @patch("auto_slopp.utils.http_requests.httpx.Client")
    def test_request_with_custom_headers(self, mock_client_class):
        """Test request with custom headers."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "OK"
        mock_response.headers = {}

        mock_client = Mock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        default_headers = {"User-Agent": "test-client"}
        client = HttpClient(headers=default_headers)

        request_headers = {"Authorization": "Bearer token123"}
        response = client.get("https://api.example.com", headers=request_headers)

        # Verify headers were merged
        expected_headers = {
            "User-Agent": "test-client",
            "Authorization": "Bearer token123",
        }
        mock_client.request.assert_called_once_with(
            method="GET",
            url="https://api.example.com",
            data=None,
            json=None,
            headers=expected_headers,
        )

    @patch("auto_slopp.utils.http_requests.httpx.Client")
    def test_http_error_response(self, mock_client_class):
        """Test handling of HTTP error responses."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_response.headers = {}

        mock_client = Mock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        client = HttpClient()
        response = client.get("https://example.com/notfound")

        assert response.status_code == 404
        assert response.content == "Not Found"
        assert response.success is False
        assert response.error is None

    @patch("auto_slopp.utils.http_requests.httpx.Client")
    def test_timeout_error(self, mock_client_class):
        """Test handling of timeout errors."""
        mock_client_class.return_value.__enter__.side_effect = httpx.TimeoutException("Request timed out")

        client = HttpClient(timeout=5.0)
        response = client.get("https://slow.example.com")

        assert response.status_code == 0
        assert response.content == ""
        assert response.success is False
        assert "timeout after 5.0s" in response.error.lower()

    @patch("auto_slopp.utils.http_requests.httpx.Client")
    def test_request_error(self, mock_client_class):
        """Test handling of request errors."""
        mock_client_class.return_value.__enter__.side_effect = httpx.RequestError("Connection failed")

        client = HttpClient()
        response = client.get("https://unreachable.example.com")

        assert response.status_code == 0
        assert response.content == ""
        assert response.success is False
        assert "request error" in response.error.lower()

    @patch("auto_slopp.utils.http_requests.httpx.Client")
    def test_unexpected_error(self, mock_client_class):
        """Test handling of unexpected errors."""
        mock_client_class.return_value.__enter__.side_effect = Exception("Unexpected error")

        client = HttpClient()
        response = client.get("https://example.com")

        assert response.status_code == 0
        assert response.content == ""
        assert response.success is False
        assert "unexpected error" in response.error.lower()


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_get_default_client_singleton(self):
        """Test that get_default_client returns the same instance."""
        client1 = get_default_client()
        client2 = get_default_client()

        # Should be the same instance
        assert client1 is client2

    @patch("auto_slopp.utils.http_requests.get_default_client")
    def test_get_function(self, mock_get_client):
        """Test the get() convenience function."""
        mock_client = Mock()
        mock_response = HttpResponse(status_code=200, content="OK", headers={}, success=True)
        mock_client.get.return_value = mock_response
        mock_get_client.return_value = mock_client

        response = get("https://example.com")

        mock_client.get.assert_called_once_with("https://example.com", headers=None)
        assert response == mock_response

    @patch("auto_slopp.utils.http_requests.get_default_client")
    def test_post_function(self, mock_get_client):
        """Test the post() convenience function."""
        mock_client = Mock()
        mock_response = HttpResponse(status_code=201, content="Created", headers={}, success=True)
        mock_client.post.return_value = mock_response
        mock_get_client.return_value = mock_client

        json_data = {"name": "test"}
        headers = {"Content-Type": "application/json"}
        response = post("https://api.example.com", json=json_data, headers=headers)

        mock_client.post.assert_called_once_with("https://api.example.com", data=None, json=json_data, headers=headers)
        assert response == mock_response

    @patch("auto_slopp.utils.http_requests.get_default_client")
    def test_put_function(self, mock_get_client):
        """Test the put() convenience function."""
        mock_client = Mock()
        mock_response = HttpResponse(status_code=200, content="Updated", headers={}, success=True)
        mock_client.put.return_value = mock_response
        mock_get_client.return_value = mock_client

        data = "field=value"
        response = put("https://api.example.com/1", data=data)

        mock_client.put.assert_called_once_with("https://api.example.com/1", data=data, json=None, headers=None)
        assert response == mock_response
