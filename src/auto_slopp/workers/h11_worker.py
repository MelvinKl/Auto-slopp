"""HTTP worker for making HTTP requests using h11.

This worker provides functionality to:
1. Make HTTP GET requests using h11
2. Parse HTTP responses using h11 events
3. Handle basic HTTP errors and timeouts
4. Return structured response data
"""

import logging
import socket
import time
from pathlib import Path
from typing import Any, Dict, Optional

import h11

from auto_slopp.worker import Worker


class H11Worker(Worker):
    """Worker for making HTTP requests using the h11 library.

    This worker implements basic HTTP/1.1 client functionality using h11
    for protocol-level request/response handling.
    """

    def __init__(self, timeout: int = 30):
        """Initialize the H11Worker.

        Args:
            timeout: Connection and read timeout in seconds
        """
        self.timeout = timeout
        self.logger = logging.getLogger("auto_slopp.workers.H11Worker")

    def run(self, repo_path: Path, task_path: Path) -> Dict[str, Any]:
        """Execute HTTP request based on task path configuration.

        Args:
            repo_path: Path to the repository directory (unused for HTTP worker)
            task_path: Path containing request configuration (URL or file with URLs)

        Returns:
            Dictionary containing HTTP response data and execution results
        """
        start_time = time.time()
        self.logger.info(f"H11Worker starting with task_path: {task_path}")

        # Initialize result structure
        result = {
            "worker_name": "H11Worker",
            "execution_time": 0,
            "timestamp": start_time,
            "repo_path": str(repo_path),
            "task_path": str(task_path),
            "success": False,
            "requests_made": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "responses": [],
        }

        try:
            # Determine what to request based on task_path
            urls = self._get_urls_from_task_path(task_path)
            if not urls:
                result["error"] = "No URLs found to request"
                return result

            # Make HTTP requests for each URL
            for url in urls:
                response_data = self._make_http_request(url)
                result["responses"].append(response_data)
                result["requests_made"] += 1

                if response_data["success"]:
                    result["successful_requests"] += 1
                else:
                    result["failed_requests"] += 1

            # Mark as successful if at least one request succeeded
            result["success"] = result["successful_requests"] > 0

        except Exception as e:
            self.logger.error(f"Unexpected error in H11Worker: {e}")
            result["error"] = f"Unexpected error: {str(e)}"

        result["execution_time"] = time.time() - start_time
        self._log_completion_summary(result)

        return result

    def _get_urls_from_task_path(self, task_path: Path) -> list[str]:
        """Extract URLs from task path.

        Args:
            task_path: Path containing URL information

        Returns:
            List of URLs to request
        """
        urls = []

        if task_path.is_file():
            # Read URLs from file
            try:
                content = task_path.read_text().strip()
                urls = [line.strip() for line in content.split("\n") if line.strip()]
            except Exception as e:
                self.logger.error(f"Failed to read URLs from file {task_path}: {e}")
        else:
            # If task_path doesn't exist or is directory, use a default example URL
            urls = ["http://httpbin.org/get"]
            self.logger.info(f"No file found at {task_path}, using example URL: {urls[0]}")

        return urls

    def _make_http_request(self, url: str) -> Dict[str, Any]:
        """Make an HTTP GET request using h11.

        Args:
            url: URL to request

        Returns:
            Dictionary containing request response data
        """
        result = {
            "url": url,
            "success": False,
            "status_code": None,
            "headers": {},
            "body": "",
            "error": None,
            "response_time": 0,
        }

        start_time = time.time()
        try:
            # Parse URL
            if not url.startswith(("http://", "https://")):
                url = "http://" + url

            if "://" not in url:
                raise ValueError(f"Invalid URL format: {url}")

            # Extract host and path from URL
            parts = url.split("://", 1)[1].split("/", 1)
            host = parts[0]
            path = "/" + parts[1] if len(parts) > 1 else "/"

            # Handle port specification
            if ":" in host:
                host, port_str = host.split(":", 1)
                port = int(port_str)
            else:
                port = 80 if url.startswith("http://") else 443

            # Create h11 connection
            conn = h11.Connection(our_role=h11.CLIENT)

            # Create HTTP GET request
            request = h11.Request(
                method="GET",
                target=path,
                headers=[
                    ("Host", host),
                    ("User-Agent", "auto-slopp-h11-worker/1.0"),
                    ("Accept", "*/*"),
                    ("Connection", "close"),
                ],
            )

            # Connect to server
            sock = socket.create_connection((host, port), timeout=self.timeout)

            try:
                # Send request
                self._send_data(conn, sock, request)
                self._send_data(conn, sock, h11.EndOfMessage())

                # Receive response
                response_data = self._receive_response(conn, sock)

                result.update(response_data)
                result["success"] = True

            finally:
                sock.close()

            result["response_time"] = time.time() - start_time
            self.logger.info(f"Successfully completed request to {url} in {result['response_time']:.2f}s")

        except Exception as e:
            result["error"] = str(e)
            result["response_time"] = time.time() - start_time
            self.logger.error(f"Failed to request {url}: {e}")

        return result

    def _send_data(self, conn: h11.Connection, sock: socket.socket, event: h11.Event) -> None:
        """Send h11 event through socket.

        Args:
            conn: h11 connection object
            sock: socket to send data through
            event: h11 event to send
        """
        data = conn.send(event)
        if data:
            sock.sendall(data)

    def _receive_response(self, conn: h11.Connection, sock: socket.socket) -> Dict[str, Any]:
        """Receive and parse HTTP response using h11.

        Args:
            conn: h11 connection object
            sock: socket to receive data from

        Returns:
            Dictionary containing parsed response data
        """
        response_data = {
            "status_code": None,
            "headers": {},
            "body": "",
        }

        buffer = b""
        headers_received = False

        while True:
            # Receive data from socket
            chunk = sock.recv(4096)
            if not chunk:
                break

            buffer += chunk
            conn.receive_data(chunk)

            # Process events
            while True:
                event = conn.next_event()
                if event is h11.NEED_DATA:
                    break
                elif isinstance(event, h11.Response):
                    response_data["status_code"] = event.status_code
                    response_data["headers"] = dict(event.headers)
                    headers_received = True
                elif isinstance(event, h11.Data):
                    response_data["body"] += event.data.decode("utf-8", errors="replace")
                elif isinstance(event, h11.EndOfMessage):
                    return response_data

        # If we get here, connection was closed prematurely
        if not headers_received and buffer:
            # Try to parse partial response for debugging
            try:
                text = buffer.decode("utf-8", errors="replace")
                if "\r\n\r\n" in text:
                    headers_part = text.split("\r\n\r\n")[0]
                    response_data["body"] = f"Partial response:\n{headers_part}"
            except UnicodeDecodeError, ValueError:
                pass

        return response_data

    def _log_completion_summary(self, result: Dict[str, Any]) -> None:
        """Log completion summary.

        Args:
            result: Final result dictionary
        """
        self.logger.info(
            f"H11Worker completed. "
            f"Requests: {result['requests_made']}, "
            f"Successful: {result['successful_requests']}, "
            f"Failed: {result['failed_requests']}, "
            f"Total time: {result['execution_time']:.2f}s"
        )
