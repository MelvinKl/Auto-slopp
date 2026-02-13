from abc import ABC, abstractmethod
from pathlib import Path


class Worker(ABC):
    """Base worker class."""

    name: str = "base"

    @abstractmethod
    def run(self, repo_path: Path, task_path: Path) -> dict:
        """Run the worker with given paths."""
        pass
