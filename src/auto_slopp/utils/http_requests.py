"""HTTP request utilities for workers.

This module provides simple HTTP request functions using httpx
for making web requests from workers.
"""

import logging
from typing import Any, Dict, Optional, Union

import httpx
from httpx._types import RequestData
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class HttpResponse(BaseModel):
    """HTTP response wrapper with useful metadata."""

    status_code: int = Field(description="HTTP status code")
    content: str = Field(description="Response content as text")
    headers: Dict[str, str] = Field(description="Response headers")
    success: bool = Field(description="Whether the request was successful (2xx status)")
    error: Optional[str] = Field(default=None, description="Error message if request failed")


class HttpClient:
    """Simple HTTP client for making web requests."""

    def __init__(
        self,
        timeout: float = 30.0,
        headers: Optional[Dict[str, str]] = None,
        follow_redirects: bool = True,
    ):
        """Initialize HTTP client.

        Args:
            timeout: Request timeout in seconds
            headers: Default headers to include with all requests
            follow_redirects: Whether to follow HTTP redirects
        """
        self.timeout = timeout
        self.default_headers = headers or {}
        self.follow_redirects = follow_redirects

    def get(self, url: str, headers: Optional[Dict[str, str]] = None) -> HttpResponse:
        """Make a GET request.

        Args:
            url: URL to request
            data: Request data (form data, bytes, etc.)
            json: JSON data to send
            headers: Additional headers for this request

        Returns:
            HttpResponse with the result
        """
        return self._make_request("GET", url, headers=headers)

    def post(
        self,
        url: str,
        data: Optional[RequestData] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> HttpResponse:
        """Make a POST request.

        Args:
            url: URL to request
            data: Form data to send
            json: JSON data to send
            headers: Additional headers for this request

        Returns:
            HttpResponse with the result
        """
        return self._make_request("POST", url, data=data, json=json, headers=headers)

    def put(
        self,
        url: str,
        data: Optional[RequestData] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> HttpResponse:
        """Make a PUT request.

        Args:
            url: URL to request
            data: Form data to send
            json: JSON data to send
            headers: Additional headers for this request

        Returns:
            HttpResponse with the result
        """
        return self._make_request("PUT", url, data=data, json=json, headers=headers)

    def _make_request(
        self,
        method: str,
        url: str,
        data: Optional[RequestData] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> HttpResponse:
        """Make an HTTP request.

        Args:
            method: HTTP method (GET, POST, PUT, etc.)
            url: URL to request
            data: Form data to send
            json: JSON data to send
            headers: Additional headers for this request

        Returns:
            HttpResponse with the result
        """
        # Merge default headers with request-specific headers
        request_headers = {**self.default_headers}
        if headers:
            request_headers.update(headers)

        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=self.follow_redirects) as client:
                response = client.request(
                    method=method,
                    url=url,
                    data=data,
                    json=json,
                    headers=request_headers,
                )

                # Convert headers to regular dict
                response_headers = dict(response.headers)

                return HttpResponse(
                    status_code=response.status_code,
                    content=response.text,
                    headers=response_headers,
                    success=200 <= response.status_code < 300,
                )

        except httpx.TimeoutException as e:
            error_msg = f"Request timeout after {self.timeout}s: {str(e)}"
            logger.error(error_msg)
            return HttpResponse(status_code=0, content="", headers={}, success=False, error=error_msg)

        except httpx.RequestError as e:
            error_msg = f"Request error: {str(e)}"
            logger.error(error_msg)
            return HttpResponse(status_code=0, content="", headers={}, success=False, error=error_msg)

        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            return HttpResponse(status_code=0, content="", headers={}, success=False, error=error_msg)


# Default client instance for simple use
_default_client: Optional[HttpClient] = None


def get_default_client() -> HttpClient:
    """Get the default HTTP client instance."""
    global _default_client
    if _default_client is None:
        _default_client = HttpClient()
    return _default_client


def get(url: str, headers: Optional[Dict[str, str]] = None) -> HttpResponse:
    """Make a simple GET request using the default client.

    Args:
        url: URL to request
        headers: Additional headers for this request

    Returns:
        HttpResponse with the result
    """
    client = get_default_client()
    return client.get(url, headers=headers)


def post(
    url: str,
    data: Optional[RequestData] = None,
    json: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
) -> HttpResponse:
    """Make a simple POST request using the default client.

    Args:
        url: URL to request
        data: Form data to send
        json: JSON data to send
        headers: Additional headers for this request

    Returns:
        HttpResponse with the result
    """
    client = get_default_client()
    return client.post(url, data=data, json=json, headers=headers)


def put(
    url: str,
    data: Optional[RequestData] = None,
    json: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
) -> HttpResponse:
    """Make a simple PUT request using the default client.

    Args:
        url: URL to request
        data: Form data to send
        json: JSON data to send
        headers: Additional headers for this request

    Returns:
        HttpResponse with the result
    """
    client = get_default_client()
    return client.put(url, data=data, json=json, headers=headers)
