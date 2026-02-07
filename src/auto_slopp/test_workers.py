"""Sample worker for testing discovery mechanism."""

from pathlib import Path

from auto_slopp.worker import Worker


class TestWorker(Worker):
    """A test worker implementation."""

    def run(self, repo_path: Path, task_path: Path) -> None:
        """Run the test worker.

        Args:
            repo_path: Path to the repository
            task_path: Path to the task
        """
        print(f"TestWorker running on {repo_path} with {task_path}")


class AnotherTestWorker(Worker):
    """Another test worker implementation."""

    def run(self, repo_path: Path, task_path: Path) -> str:
        """Run another test worker.

        Args:
            repo_path: Path to the repository
            task_path: Path to the task

        Returns:
            A string result
        """
        return f"AnotherTestWorker completed for {repo_path}"


class NotAWorker:
    """A class that doesn't inherit from Worker - should not be discovered."""

    def some_method(self) -> None:
        """A regular method."""
        pass
