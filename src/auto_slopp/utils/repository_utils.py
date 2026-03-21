"""Repository validation utilities for auto-slopp workers.

This module provides utility functions for validating repository directories
and ensuring they are proper git repositories.
"""

from pathlib import Path
from typing import Any, Dict, List

from auto_slopp.utils.git_operations import (
    get_ahead_behind,
    get_current_branch,
    get_default_branch,
    get_remotes,
    has_changes,
    is_bare_repository,
)


def is_git_repository(repo_dir: Path) -> bool:
    """Check if a directory is a git repository.

    Args:
        repo_dir: Path to the directory to check

    Returns:
        True if the directory is a git repository, False otherwise
    """
    try:
        git_dir = repo_dir / ".git"
        # Check for .git as a directory (normal repo) or as a file (worktree)
        if git_dir.is_dir():
            return True
        if git_dir.is_file():
            return True
        return False
    except Exception:
        return False


def validate_repository(repo_dir: Path) -> Dict[str, Any]:
    """Validate a repository directory and return status information.

    Args:
        repo_dir: Path to the repository directory to validate

    Returns:
        Dictionary containing validation results and repository information
    """
    result = {
        "path": str(repo_dir),
        "exists": repo_dir.exists(),
        "is_directory": repo_dir.is_dir() if repo_dir.exists() else False,
        "is_git_repo": False,
        "has_remotes": False,
        "remotes": [],
        "default_branch": None,
        "is_bare": False,
        "errors": [],
        "valid": False,
    }

    if not result["exists"]:
        result["errors"].append("Directory does not exist")
        return result

    if not result["is_directory"]:
        result["errors"].append("Path is not a directory")
        return result

    # Check if it's a git repository
    if not is_git_repository(repo_dir):
        result["errors"].append("Not a git repository (no .git directory)")
        return result

    result["is_git_repo"] = True

    try:
        result["is_bare"] = is_bare_repository(repo_dir)

        result["remotes"] = get_remotes(repo_dir)
        result["has_remotes"] = len(result["remotes"]) > 0

        result["default_branch"] = get_default_branch(repo_dir)

        result["valid"] = len(result["errors"]) == 0 and result["is_git_repo"]

    except Exception as e:
        result["errors"].append(f"Error validating repository: {str(e)}")

    return result
