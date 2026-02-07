"""Worker base class for auto-slopp automation system."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class Worker(ABC):
    """Abstract base class for all worker implementations.

    All workers must inherit from this class and implement the run method.
    The run method is called with repo_path and task_path parameters
    to execute the worker's specific automation task.
    """

    @abstractmethod
    def run(self, repo_path: Path, task_path: Path) -> Any:
        """Execute the worker's automation task.

        Args:
            repo_path: Path to the repository directory
            task_path: Path to the task directory or file

        Returns:
            Any result data from the worker execution
        """
        pass
