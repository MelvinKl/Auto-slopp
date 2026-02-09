"""Renovate branch testing worker for auto-slopp automation system.

This worker iterates through all directories in repo_path, checks out renovate branches,
runs tests, and uses OpenAgent to fix any failing tests.
"""

import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, List

from auto_slopp.utils.repository_utils import discover_repositories, validate_repository
from auto_slopp.worker import Worker
from auto_slopp.workers.openagent_worker import OpenAgentWorker


class RenovateTestWorker(Worker):
    """Worker for testing renovate branches and fixing failures with OpenAgent."""

    def __init__(self, timeout: int = 600):
        """Initialize the RenovateTestWorker.

        Args:
            timeout: Timeout for test execution and OpenAgent fixes in seconds
        """
        self.timeout = timeout
        self.logger = logging.getLogger("auto_slopp.workers.RenovateTestWorker")
        self.openagent_worker = OpenAgentWorker(
            agent_args=["fix", "the", "tests", "and", "push", "the", "changes"],
            timeout=timeout,
            capture_output=True,
            process_all_repos=False,
        )

    def run(self, repo_path: Path, task_path: Path) -> Dict[str, Any]:
        """Execute renovate branch testing workflow.

        Args:
            repo_path: Path to the repository directory containing subdirectories
            task_path: Path to the task directory or file (not used in this worker)

        Returns:
            Dictionary containing execution results and summary.
        """
        self.logger.info(f"RenovateTestWorker starting in {repo_path}")

        if not repo_path.exists():
            return {
                "worker_name": "RenovateTestWorker",
                "success": False,
                "error": f"Repository path does not exist: {repo_path}",
                "repositories_processed": 0,
                "repositories_tested": 0,
                "repositories_fixed": 0,
            }

        # Discover and validate repositories
        repositories = discover_repositories(repo_path, validate=True)

        results = {
            "worker_name": "RenovateTestWorker",
            "success": True,
            "repositories_processed": 0,
            "repositories_tested": 0,
            "repositories_fixed": 0,
            "repositories_with_errors": 0,
            "repositories_invalid": 0,
            "repository_results": [],
            "errors": [],
        }

        # Process only valid git repositories
        for repo_info in repositories:
            repo_dir = Path(repo_info["path"])

            self.logger.info(f"Processing repository: {repo_info['name']}")
            results["repositories_processed"] += 1

            if not repo_info.get("valid", False):
                self.logger.warning(
                    f"Skipping invalid repository: {repo_info['name']} - {repo_info.get('errors', ['Unknown error'])}"
                )
                results["repositories_invalid"] += 1
                results["repositories_with_errors"] += 1
                results["errors"].append(
                    f"{repo_info['name']}: Invalid repository - {repo_info.get('errors', ['Unknown error'])}"
                )
                continue

            repo_result = self._process_repository(repo_dir)
            results["repository_results"].append(repo_result)

            if repo_result["success"]:
                results["repositories_tested"] += 1
                if repo_result["tests_fixed"]:
                    results["repositories_fixed"] += 1
            else:
                results["repositories_with_errors"] += 1
                results["errors"].append(
                    f"{repo_dir.name}: {repo_result.get('error', 'Unknown error')}"
                )

        # Determine overall success
        if results["repositories_with_errors"] > 0:
            results["success"] = False

        self.logger.info(
            f"RenovateTestWorker completed. Processed: {results['repositories_processed']}, "
            f"Valid: {results['repositories_processed'] - results['repositories_invalid']}, "
            f"Invalid: {results['repositories_invalid']}, "
            f"Tested: {results['repositories_tested']}, Fixed: {results['repositories_fixed']}, "
            f"Errors: {results['repositories_with_errors']}"
        )

        return results

    def _process_repository(self, repo_dir: Path) -> Dict[str, Any]:
        """Process a single repository directory.

        Args:
            repo_dir: Path to the repository directory

        Returns:
            Dictionary containing processing results for this repository.
        """
        result = {
            "repository": repo_dir.name,
            "path": str(repo_dir),
            "success": False,
            "branches_checked_out": [],
            "test_results": [],
            "tests_fixed": False,
            "error": None,
        }

        try:
            # Get all renovate branches
            renovate_branches = self._get_renovate_branches(repo_dir)
            result["branches_checked_out"] = renovate_branches

            if not renovate_branches:
                result["error"] = "No renovate branches found"
                return result

            # Test each renovate branch
            for branch in renovate_branches:
                self.logger.info(f"Testing branch {branch} in {repo_dir.name}")

                # Checkout the branch
                if not self._checkout_branch(repo_dir, branch):
                    result["error"] = f"Failed to checkout branch {branch}"
                    continue

                # Run tests
                test_result = self._run_tests(repo_dir)
                result["test_results"].append(
                    {
                        "branch": branch,
                        "success": test_result["success"],
                        "output": test_result.get("output", ""),
                        "error": test_result.get("error"),
                    }
                )

                # If tests failed, use OpenAgent to fix them
                if not test_result["success"]:
                    self.logger.info(
                        f"Tests failed for {branch} in {repo_dir.name}, using OpenAgent to fix"
                    )
                    fix_result = self._fix_tests_with_openagent(repo_dir)
                    if fix_result["success"]:
                        result["tests_fixed"] = True
                        # Re-run tests to verify fix
                        verify_result = self._run_tests(repo_dir)
                        result["test_results"][-1]["fix_success"] = verify_result[
                            "success"
                        ]
                        result["test_results"][-1]["fix_output"] = verify_result.get(
                            "output", ""
                        )
                    else:
                        result["test_results"][-1]["fix_success"] = False
                        result["test_results"][-1]["fix_error"] = fix_result.get(
                            "error", "Unknown fix error"
                        )
                else:
                    result["test_results"][-1]["fix_success"] = True  # No fix needed

            result["success"] = True

        except Exception as e:
            self.logger.error(f"Error processing repository {repo_dir.name}: {str(e)}")
            result["error"] = str(e)

        return result

    def _get_renovate_branches(self, repo_dir: Path) -> List[str]:
        """Get list of renovate branches in the repository.

        Args:
            repo_dir: Path to the repository directory

        Returns:
            List of renovate branch names
        """
        try:
            result = subprocess.run(
                ["git", "branch", "-r"],
                cwd=repo_dir,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                self.logger.error(
                    f"Failed to list branches in {repo_dir.name}: {result.stderr}"
                )
                return []

            branches = []
            for line in result.stdout.strip().split("\n"):
                branch = line.strip()
                if "renovate" in branch.lower():
                    # Remove 'origin/' prefix if present
                    if branch.startswith("origin/"):
                        branch = branch[7:]
                    branches.append(branch)

            return branches

        except subprocess.TimeoutExpired:
            self.logger.error(f"Timeout getting branches from {repo_dir.name}")
            return []
        except Exception as e:
            self.logger.error(f"Error getting branches from {repo_dir.name}: {str(e)}")
            return []

    def _checkout_branch(self, repo_dir: Path, branch: str) -> bool:
        """Checkout a specific branch in the repository.

        Args:
            repo_dir: Path to the repository directory
            branch: Branch name to checkout

        Returns:
            True if checkout successful, False otherwise
        """
        try:
            # Fetch latest changes
            subprocess.run(
                ["git", "fetch", "origin"],
                cwd=repo_dir,
                capture_output=True,
                text=True,
                timeout=60,
            )

            # Checkout the branch
            result = subprocess.run(
                ["git", "checkout", branch],
                cwd=repo_dir,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                self.logger.error(
                    f"Failed to checkout {branch} in {repo_dir.name}: {result.stderr}"
                )
                return False

            # Pull latest changes for the branch
            subprocess.run(
                ["git", "pull", "origin", branch],
                cwd=repo_dir,
                capture_output=True,
                text=True,
                timeout=60,
            )

            self.logger.info(f"Successfully checked out {branch} in {repo_dir.name}")
            return True

        except subprocess.TimeoutExpired:
            self.logger.error(f"Timeout checking out {branch} in {repo_dir.name}")
            return False
        except Exception as e:
            self.logger.error(
                f"Error checking out {branch} in {repo_dir.name}: {str(e)}"
            )
            return False

    def _run_tests(self, repo_dir: Path) -> Dict[str, Any]:
        """Run make test in the repository.

        Args:
            repo_dir: Path to the repository directory

        Returns:
            Dictionary containing test execution results
        """
        try:
            result = subprocess.run(
                ["make", "test"],
                cwd=repo_dir,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )

            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None,
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "error": f"Test execution timed out after {self.timeout} seconds",
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": f"Error running tests: {str(e)}",
            }

    def _fix_tests_with_openagent(self, repo_dir: Path) -> Dict[str, Any]:
        """Use OpenAgent to fix failing tests.

        Args:
            repo_dir: Path to the repository directory

        Returns:
            Dictionary containing OpenAgent execution results
        """
        try:
            # Create a dummy task path for OpenAgent
            task_path = repo_dir / "fix_tests.task"

            # Run OpenAgent to fix tests
            result = self.openagent_worker.run(repo_dir, task_path)

            return {
                "success": result.get("success", False),
                "output": result.get("stdout", ""),
                "error": result.get("stderr") or result.get("error"),
                "return_code": result.get("return_code", -1),
            }

        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": f"Error running OpenAgent: {str(e)}",
            }
