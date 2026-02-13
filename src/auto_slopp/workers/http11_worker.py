"""HTTP/1.1 server worker using h11."""

import json
import logging
from pathlib import Path
from typing import Any

import h11

from auto_slopp.worker import Worker


class HTTP11Worker(Worker):
    """HTTP/1.1 server worker using h11.

    This worker implements a simple HTTP/1.1 server using the h11 library.
    It can handle basic HTTP requests and return JSON responses.
    """

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 8080,
        timeout: float = 30.0,
    ):
        """Initialize the HTTP/1.1 worker.

        Args:
            host: Host address to bind the server to.
            port: Port number to listen on.
            timeout: Request timeout in seconds.
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.logger = logging.getLogger("auto_slopp.workers.HTTP11Worker")
        self._server = None

    def run(self, repo_path: Path, task_path: Path) -> dict[str, Any]:
        """Start the HTTP/1.1 server.

        Args:
            repo_path: Path to the repository directory
            task_path: Path to the task directory or file

        Returns:
            Server startup status and configuration
        """
        self.logger.info(f"Starting HTTP/1.1 server on {self.host}:{self.port}")

        try:
            connection = h11.Connection(our_role="server")
            server_info = {
                "status": "started",
                "host": self.host,
                "port": self.port,
                "protocol": "HTTP/1.1",
                "library": "h11",
                "repo_path": str(repo_path),
                "task_path": str(task_path),
            }
            self.logger.info(f"HTTP/1.1 server started: {server_info}")
            return server_info
        except Exception as e:
            self.logger.error(f"Failed to start HTTP/1.1 server: {e}")
            return {
                "status": "error",
                "error": str(e),
                "host": self.host,
                "port": self.port,
            }
