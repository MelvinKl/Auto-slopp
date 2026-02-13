"""HTTP worker for making HTTP requests using h11.

This worker provides functionality to:
1. Make HTTP GET requests using h11
2. Parse HTTP responses using h11 events
3. Handle basic HTTP errors and timeouts
4. Return structured response data
"""

import logging
import socket
import ssl
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

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
            urls = self._get_urls_from_task_path(task_path)
            if not urls:
                result["error"] = "No URLs found to request"
                return result

            for url in urls:
                response_data = self._make_http_request(url)
                result["responses"].append(response_data)
                result["requests_made"] += 1

                if response_data["success"]:
                    result["successful_requests"] += 1
                else:
                    result["failed_requests"] += 1

            result["success"] = result["successful_requests"] > 0

        except Exception as e:
            self.logger.error(f"Unexpected error in H11Worker: {e}")
            result["error"] = f"Unexpected error: {str(e)}"

        result["execution_time"] = time.time() - start_time
        self._log_completion_summary(result)

        return result

    def _get_urls_from_task_path(self, task_path: Path) -> List[str]:
        """Extract URLs from task path.

        Args:
            task_path: Path containing URL information

        Returns:
            List of URLs to request
        """
        urls = []

        if not task_path.exists():
            url = self._parse_url_from_path(str(task_path))
            if url:
                urls.append(url)
            return urls

        if task_path.is_file():
            content = task_path.read_text().strip()
            for line in content.splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    url = self._parse_url_from_path(line)
                    if url:
                        urls.append(url)
        else:
            url = self._parse_url_from_path(str(task_path))
            if url:
                urls.append(url)

        return urls

    def _parse_url_from_path(self, path_or_url: str) -> Optional[str]:
        """Parse URL from path or direct URL string.

        Args:
            path_or_url: Path string or URL

        Returns:
            Parsed URL or None
        """
        path_or_url = path_or_url.strip()

        if path_or_url.startswith(("http://", "https://")):
            return path_or_url

        return None

    def _make_http_request(self, url: str) -> Dict[str, Any]:
        """Make HTTP request using h11.

        Args:
            url: URL to request

        Returns:
            Dictionary containing response data
        """
        response_data = {
            "url": url,
            "success": False,
            "status_code": None,
            "body": "",
            "error": None,
        }

        try:
            parsed = self._parse_url(url)
            if not parsed:
                response_data["error"] = "Invalid URL"
                return response_data

            host, port, path, use_ssl = parsed
            response_data = self._send_http_request(host, port, path, use_ssl, response_data)

        except Exception as e:
            response_data["error"] = str(e)

        return response_data

    def _parse_url(self, url: str) -> Optional[tuple]:
        """Parse URL into host, port, path, and SSL flag.

        Args:
            url: URL to parse

        Returns:
            Tuple of (host, port, path, use_ssl) or None
        """
        use_ssl = False

        if url.startswith("https://"):
            host = url[8:]
            port = 443
            use_ssl = True
        elif url.startswith("http://"):
            host = url[7:]
            port = 80
        else:
            return None

        if "/" in host:
            path = host.split("/", 1)[1]
            host = host.split("/")[0]
        else:
            path = ""

        if ":" in host:
            parts = host.rsplit(":", 1)
            host = parts[0]
            try:
                port = int(parts[1])
            except ValueError:
                pass

        path = path if path else "/"

        return (host, port, path, use_ssl)

    def _send_http_request(
        self,
        host: str,
        port: int,
        path: str,
        use_ssl: bool,
        response_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Send HTTP request using raw socket with h11 protocol.

        Args:
            host: Hostname
            port: Port number
            path: Request path
            use_ssl: Whether to use SSL
            response_data: Response data dictionary to update

        Returns:
            Updated response data dictionary
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            sock.connect((host, port))

            if use_ssl:
                ctx = ssl.create_default_context()
                sock = ctx.wrap_socket(sock, server_hostname=host)

            conn = h11.Connection(our_role=h11.CLIENT)

            request = h11.Request(
                method="GET",
                target=path,
                headers=[
                    ("Host", host),
                    ("User-Agent", "H11Worker/1.0"),
                    ("Accept", "*/*"),
                ],
            )

            data = conn.send(request)
            if data:
                sock.sendall(data)

            data = conn.send(h11.EndOfMessage())
            if data:
                sock.sendall(data)

            response_body = b""
            while conn.our_state != h11.DONE or conn.their_state != h11.DONE:
                data = sock.recv(4096)
                if not data:
                    break
                response_body += data
                events = conn.receive_data(data)
                for event in events:
                    if isinstance(event, h11.Response):
                        response_data["status_code"] = event.status_code
                    elif isinstance(event, h11.Data):
                        response_data["body"] += event.data.decode("utf-8", errors="replace")
                    elif isinstance(event, h11.ConnectionClosed):
                        break

            sock.close()
            response_data["success"] = response_data.get("status_code") == 200

        except socket.timeout:
            response_data["error"] = "Connection timeout"
        except socket.error as e:
            response_data["error"] = f"Socket error: {str(e)}"
        except Exception as e:
            response_data["error"] = f"Request error: {str(e)}"

        return response_data

    def _log_completion_summary(self, result: Dict[str, Any]) -> None:
        """Log completion summary.

        Args:
            result: Worker result dictionary
        """
        self.logger.info(
            f"H11Worker completed: {result['successful_requests']}/{result['requests_made']} "
            f"successful requests in {result['execution_time']:.2f}s"
        )
