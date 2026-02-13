"""Distlib worker for analyzing Python package distributions.

This worker uses distlib to inspect and analyze Python package distributions
within a repository, extracting metadata and distribution information.
"""

import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from auto_slopp.worker import Worker


class DistlibWorker(Worker):
    """Worker for analyzing Python package distributions using distlib.

    This worker scans a repository for Python packages and uses distlib
    to extract distribution metadata such as name, version, dependencies,
    and other package information.
    """

    def __init__(self, include_wheels: bool = True, include_sdists: bool = True):
        """Initialize the distlib worker.

        Args:
            include_wheels: Whether to include wheel distributions
            include_sdists: Whether to include source distributions
        """
        self.include_wheels = include_wheels
        self.include_sdists = include_sdists
        self.logger = logging.getLogger("auto_slopp.workers.DistlibWorker")

    def run(self, repo_path: Path, task_path: Path) -> Dict[str, Any]:
        """Execute distlib package analysis for a repository.

        Args:
            repo_path: Path to the repository directory
            task_path: Path to the task directory or file (unused in worker)

        Returns:
            Dictionary containing package distribution analysis results.
        """
        start_time = time.time()
        self.logger.info(f"Starting distlib package analysis for {repo_path}")

        validation_result = self._validate_input_path(repo_path, task_path, start_time)
        if validation_result:
            return validation_result

        results = self._create_results_dict(start_time, repo_path, task_path)

        packages_found = self._analyze_packages(repo_path)
        results["packages_found"] = len(packages_found)
        results["packages"] = packages_found
        results["success"] = True

        results["execution_time"] = time.time() - start_time
        self._log_completion_summary(results)

        return results

    def _validate_input_path(self, repo_path: Path, task_path: Path, start_time: float) -> Optional[Dict[str, Any]]:
        """Validate the input repository path.

        Args:
            repo_path: Path to validate
            task_path: Task path (for result structure)
            start_time: Start time for error result

        Returns:
            Error result if validation fails, None otherwise
        """
        if not repo_path.exists():
            return {
                "worker_name": "DistlibWorker",
                "execution_time": time.time() - start_time,
                "repo_path": str(repo_path),
                "task_path": str(task_path),
                "success": False,
                "error": f"Repository path does not exist: {repo_path}",
                "packages_found": 0,
                "packages": [],
            }
        return None

    def _create_results_dict(self, start_time: float, repo_path: Path, task_path: Path) -> Dict[str, Any]:
        """Create the initial results dictionary.

        Args:
            start_time: Start time of execution
            repo_path: Repository path
            task_path: Task path

        Returns:
            Initialized results dictionary
        """
        return {
            "worker_name": "DistlibWorker",
            "execution_time": 0,
            "repo_path": str(repo_path),
            "task_path": str(task_path),
            "include_wheels": self.include_wheels,
            "include_sdists": self.include_sdists,
            "packages_found": 0,
            "packages": [],
            "success": True,
        }

    def _analyze_packages(self, repo_path: Path) -> List[Dict[str, Any]]:
        """Analyze packages in the repository using distlib.

        Args:
            repo_path: Path to the repository directory

        Returns:
            List of package information dictionaries
        """
        packages = []

        try:
            import distlib.database

            dist_path = distlib.database.DistributionPath([str(repo_path)], include_egg=True)

            for dist in dist_path.get_distributions():
                try:
                    metadata = dist.metadata
                    package_info = {
                        "name": metadata.get("Name", "unknown"),
                        "version": metadata.get("Version", "unknown"),
                        "summary": metadata.get("Summary", ""),
                    }
                    packages.append(package_info)
                    self.logger.debug(f"Found package: {package_info['name']} version {package_info['version']}")
                except Exception as e:
                    self.logger.debug(f"Could not read metadata for {dist}: {e}")

        except Exception as e:
            self.logger.warning(f"Error analyzing packages with distlib: {e}")

        return packages

    def _log_completion_summary(self, results: Dict[str, Any]) -> None:
        """Log completion summary.

        Args:
            results: Final results dictionary
        """
        self.logger.info(
            f"DistlibWorker completed. Packages found: {results['packages_found']}, "
            f"Execution time: {results['execution_time']:.2f}s"
        )
