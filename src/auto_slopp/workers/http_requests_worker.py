"""HTTP requests worker for making web API calls.

This worker provides a simple way to make HTTP requests as part of automation tasks.
It can be used to call APIs, fetch web content, or interact with web services.
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from auto_slopp.worker import Worker
from auto_slopp.utils.http_requests import get, post, put, HttpClient

logger = logging.getLogger(__name__)


class HttpRequestsWorker(Worker):
    """Worker for making HTTP requests to external APIs and web services."""

    def __init__(
        self,
        method: str = "GET",
        url: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        timeout: float = 30.0,
    ):
        """Initialize the HTTP requests worker.

        Args:
            method: HTTP method (GET, POST, PUT, etc.)
            url: URL to request (can be None if read from task file)
            headers: HTTP headers to include
            data: Form data to send
            json_data: JSON data to send
            timeout: Request timeout in seconds
        """
        self.method = method.upper()
        self.url = url
        self.headers = headers
        self.data = data
        self.json_data = json_data
        self.timeout = timeout
        self.client = HttpClient(timeout=timeout, headers=headers)

    def run(self, repo_path: Path, task_path: Path) -> Dict[str, Any]:
        """Execute HTTP request and return response.

        Args:
            repo_path: Path to the repository directory (not used by this worker)
            task_path: Path to task file or directory

        Returns:
            Dictionary containing the HTTP response details
        """
        # Read URL from task file if not provided
        url = self.url
        if url is None and task_path.is_file():
            try:
                url = task_path.read_text(encoding="utf-8").strip()
                if not url:
                    raise ValueError("Task file is empty")
            except Exception as e:
                error_msg = f"Failed to read URL from task file {task_path}: {str(e)}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "status_code": 0,
                    "content": "",
                    "headers": {},
                }

        if not url:
            error_msg = "No URL provided and could not read from task file"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "status_code": 0,
                "content": "",
                "headers": {},
            }

        logger.info(f"Making {self.method} request to {url}")

        # Make the HTTP request based on method
        try:
            if self.method == "GET":
                response = get(url, headers=self.headers)
            elif self.method == "POST":
                response = post(
                    url, data=self.data, json=self.json_data, headers=self.headers
                )
            elif self.method == "PUT":
                response = put(
                    url, data=self.data, json=self.json_data, headers=self.headers
                )
            else:
                # Use client directly for other methods
                response = self.client._make_request(
                    method=self.method,
                    url=url,
                    data=self.data,
                    json=self.json_data,
                    headers=self.headers,
                )

            # Log response details
            if response.success:
                logger.info(f"Request successful: {response.status_code}")
            else:
                logger.warning(f"Request failed: {response.status_code}")

            return {
                "success": response.success,
                "status_code": response.status_code,
                "content": response.content,
                "headers": dict(response.headers),
                "error": response.error,
                "url": url,
                "method": self.method,
            }

        except Exception as e:
            error_msg = f"Unexpected error during HTTP request: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "status_code": 0,
                "content": "",
                "headers": {},
                "url": url,
                "method": self.method,
            }
