"""GitHub operations utilities for workers.

This module provides pure functions for common GitHub operations
used across different workers.
"""

import json
import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class GitHubOperationError(Exception):
    """Exception raised when GitHub operations fail."""

    pass


def _run_gh_command(
    repo_dir: Path,
    *args: str,
    check: bool = True,
    timeout: int = 30,
    capture_output: bool = True,
) -> subprocess.CompletedProcess:
    """Run a gh command in the specified repository.

    Args:
        repo_dir: Path to the git repository
        *args: GitHub CLI command arguments
        check: Whether to raise exception on non-zero return code
        timeout: Timeout for the command in seconds
        capture_output: Whether to capture output

    Returns:
        CompletedProcess instance

    Raises:
        GitHubOperationError: If gh command fails and check is True
    """
    try:
        result = subprocess.run(
            ["gh", *args],
            cwd=repo_dir,
            capture_output=capture_output,
            text=capture_output,
            check=check,
            timeout=timeout,
        )
        return result
    except subprocess.CalledProcessError as e:
        error_output = (e.stderr.strip() or e.stdout.strip()) if e.stderr or e.stdout else str(e)
        logger.error(f"GitHub command 'gh {' '.join(args)}' failed in {repo_dir}: {error_output}")
        raise GitHubOperationError(f"GitHub command failed: {error_output}")
    except (subprocess.TimeoutExpired, TimeoutError) as e:
        logger.error(f"GitHub command 'gh {' '.join(args)}' timed out in {repo_dir}")
        raise GitHubOperationError(f"GitHub command timed out: {e}")


def get_open_pr_branches(repo_dir: Path) -> List[str]:
    """Get list of branches from open PRs in the repository.

    Args:
        repo_dir: Path to the git repository

    Returns:
        List of branch names from open PRs.

    Raises:
        GitHubOperationError: If gh command fails
    """
    try:
        result = _run_gh_command(
            repo_dir,
            "pr",
            "list",
            "--state=open",
            "--json=headRefName",
            check=False,
        )

        if result.returncode != 0:
            pr_error = result.stderr.strip() or result.stdout.strip()
            logger.error(f"Failed to list PRs in {repo_dir.name}: {pr_error}")
            return []

        prs = json.loads(result.stdout)
        branches = [pr["headRefName"] for pr in prs]

        return branches

    except GitHubOperationError as e:
        logger.error(f"Error getting PRs from {repo_dir.name}: {str(e)}")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse PR list JSON from {repo_dir.name}: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error getting PRs from {repo_dir.name}: {str(e)}")
        return []
