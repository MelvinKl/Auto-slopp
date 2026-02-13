"""Example worker implementations for auto-slopp."""

from pathlib import Path
from typing import Any, Dict, List

from auto_slopp.worker import Worker


class Apipkg(Worker):
    """Worker that inspects Python packages for API-related information.

    Scans a repository for Python packages and collects information about
    their structure, including __init__.py files, module counts, and
    package metadata.
    """

    def __init__(self, include_hidden: bool = False):
        """Initialize the Apipkg worker.

        Args:
            include_hidden: Whether to include hidden files and directories
        """
        self.include_hidden = include_hidden

    def run(self, repo_path: Path, task_path: Path) -> Dict[str, Any]:
        """Scan repository for Python packages and API information.

        Args:
            repo_path: Path to the repository directory
            task_path: Path to the task directory or file (unused)

        Returns:
            Dictionary containing package information
        """
        if not repo_path.exists():
            return {"error": f"Repository path does not exist: {repo_path}"}

        packages = self._discover_packages(repo_path)

        return {
            "worker_name": "Apipkg",
            "repo_path": str(repo_path),
            "package_count": len(packages),
            "packages": packages,
        }

    def _discover_packages(self, base_path: Path) -> List[Dict[str, Any]]:
        """Discover Python packages in the given directory.

        Args:
            base_path: Directory to scan for packages

        Returns:
            List of package information dictionaries
        """
        packages = []

        for item in base_path.rglob("__init__.py"):
            if not self.include_hidden and any(part.startswith(".") for part in item.parts):
                continue

            package_dir = item.parent
            modules = self._count_modules(package_dir)

            packages.append(
                {
                    "name": package_dir.name,
                    "path": str(package_dir.relative_to(base_path)),
                    "module_count": modules,
                }
            )

        return packages

    def _count_modules(self, package_dir: Path) -> int:
        """Count Python modules in a package directory.

        Args:
            package_dir: Directory to count modules in

        Returns:
            Number of Python modules
        """
        count = 0
        for item in package_dir.iterdir():
            if item.suffix == ".py" and (self.include_hidden or not item.name.startswith(".")):
                count += 1
        return count
