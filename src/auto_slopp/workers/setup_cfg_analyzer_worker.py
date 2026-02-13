"""Worker for analyzing setup.cfg files from popular Python packages."""

import logging
from pathlib import Path
from typing import Any, Dict, List

from auto_slopp.utils.setup_cfg_analyzer import (
    POPULAR_PACKAGES_SETUP_CFG,
    fetch_all_popular_packages_setup_cfg,
    fetch_and_parse_setup_cfg,
)
from auto_slopp.worker import Worker


class SetupCfgAnalyzerWorker(Worker):
    """Worker for analyzing setup.cfg files from popular Python packages.

    This worker fetches and parses setup.cfg files from popular Python packages
    to understand their configuration patterns, entry points, and metadata.
    """

    def __init__(self, package_filter: list[str] | None = None):
        """Initialize the SetupCfgAnalyzerWorker.

        Args:
            package_filter: Optional list of package names to filter.
                           If None, all packages are processed.
        """
        self.package_filter = package_filter
        self.logger = logging.getLogger("auto_slopp.workers.SetupCfgAnalyzerWorker")

    def run(self, repo_path: Path, task_path: Path) -> Dict[str, Any]:
        """Execute the setup.cfg analysis.

        Args:
            repo_path: Path to repository (unused)
            task_path: Path to task directory (unused)

        Returns:
            Dictionary containing analysis results
        """
        self.logger.info("Starting setup.cfg analysis for popular packages")

        if self.package_filter:
            packages_to_process = [
                (name, url) for name, url in POPULAR_PACKAGES_SETUP_CFG if name in self.package_filter
            ]
        else:
            packages_to_process = POPULAR_PACKAGES_SETUP_CFG

        results = {
            "worker_name": "SetupCfgAnalyzerWorker",
            "packages_analyzed": 0,
            "packages_succeeded": 0,
            "packages_failed": 0,
            "package_details": [],
        }

        for package_name, url in packages_to_process:
            self.logger.info(f"Analyzing setup.cfg for {package_name}")
            info = fetch_and_parse_setup_cfg(url, package_name)

            results["packages_analyzed"] += 1

            if info.error:
                results["packages_failed"] += 1
                self.logger.warning(f"Failed to analyze {package_name}: {info.error}")
            else:
                results["packages_succeeded"] += 1

            results["package_details"].append(
                {
                    "name": package_name,
                    "url": url,
                    "has_metadata": bool(info.metadata),
                    "has_options": bool(info.options),
                    "has_entry_points": bool(info.entry_points),
                    "metadata_keys": list(info.metadata.keys()) if info.metadata else [],
                    "options_keys": list(info.options.keys()) if info.options else [],
                    "entry_point_sections": list(info.entry_points.keys()) if info.entry_points else [],
                    "error": info.error,
                }
            )

        self.logger.info(
            f"Analysis complete. Analyzed: {results['packages_analyzed']}, "
            f"Succeeded: {results['packages_succeeded']}, "
            f"Failed: {results['packages_failed']}"
        )

        return results
