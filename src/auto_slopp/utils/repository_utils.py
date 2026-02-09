"""Repository validation utilities for auto-slopp workers.

This module provides utility functions for validating repository directories
and ensuring they are proper git repositories.
"""

import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def is_git_repository(repo_dir: Path) -> bool:
    """Check if a directory is a git repository.

    Args:
        repo_dir: Path to the directory to check

    Returns:
        True if the directory is a git repository, False otherwise
    """
    try:
        git_dir = repo_dir / ".git"
        return git_dir.exists() and git_dir.is_dir()
    except Exception:
        return False


def validate_repository(repo_dir: Path) -> Dict[str, any]:
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
        # Check if it's a bare repository
        result_bare = subprocess.run(
            ["git", "rev-parse", "--is-bare-repository"],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            timeout=10,
        )
        result["is_bare"] = result_bare.stdout.strip() == "true"

        # Get remotes
        remote_result = subprocess.run(
            ["git", "remote", "-v"],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            timeout=10,
        )

        if remote_result.returncode == 0:
            remotes = []
            for line in remote_result.stdout.strip().split("\n"):
                if line.strip():
                    parts = line.split("\t")
                    if len(parts) >= 2:
                        remote_name = parts[0]
                        remote_url = parts[1].split(" ")[0]
                        remotes.append({"name": remote_name, "url": remote_url})

            result["remotes"] = remotes
            result["has_remotes"] = len(remotes) > 0

        # Get default branch
        default_branch_result = subprocess.run(
            ["git", "config", "--get", "init.defaultBranch"],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            timeout=10,
        )

        if default_branch_result.returncode == 0:
            result["default_branch"] = default_branch_result.stdout.strip()
        else:
            # Fallback to common branch names
            for branch in ["main", "master", "develop"]:
                branch_result = subprocess.run(
                    ["git", "rev-parse", "--verify", branch],
                    cwd=repo_dir,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if branch_result.returncode == 0:
                    result["default_branch"] = branch
                    break

        # Mark as valid if no errors and it's a git repo
        result["valid"] = len(result["errors"]) == 0 and result["is_git_repo"]

    except subprocess.TimeoutExpired:
        result["errors"].append("Git command timed out")
    except Exception as e:
        result["errors"].append(f"Error validating repository: {str(e)}")

    return result


def discover_repositories(repo_path: Path, validate: bool = True) -> List[Dict[str, any]]:
    """Discover all git repositories in the given path.

    Args:
        repo_path: Path to search for repositories (contains subdirectories)
        validate: Whether to validate each discovered repository

    Returns:
        List of dictionaries containing repository information
    """
    repositories = []

    if not repo_path.exists():
        return repositories

    for item in repo_path.iterdir():
        if not item.is_dir():
            continue

        repo_info = {
            "name": item.name,
            "path": str(item),
            "is_git_repo": is_git_repository(item),
        }

        if validate:
            validation = validate_repository(item)
            repo_info.update(validation)
        else:
            repo_info["valid"] = repo_info["is_git_repo"]

        repositories.append(repo_info)

    return repositories


def get_repository_status(repo_dir: Path) -> Dict[str, any]:
    """Get the git status of a repository.

    Args:
        repo_dir: Path to the repository directory

    Returns:
        Dictionary containing repository status information
    """
    if not is_git_repository(repo_dir):
        return {
            "valid": False,
            "error": "Not a git repository",
        }

    try:
        # Get current branch
        branch_result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            timeout=10,
        )

        # Get status
        status_result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            timeout=10,
        )

        # Get ahead/behind info
        sync_result = subprocess.run(
            ["git", "rev-list", "--count", "--left-right", "HEAD...@{u}"],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            timeout=10,
        )

        status = {
            "valid": True,
            "current_branch": branch_result.stdout.strip() if branch_result.returncode == 0 else None,
            "is_clean": len(status_result.stdout.strip()) == 0,
            "changed_files": [],
            "ahead": 0,
            "behind": 0,
        }

        # Parse changed files
        if status_result.returncode == 0:
            for line in status_result.stdout.strip().split("\n"):
                if line.strip():
                    status_code = line[:2]
                    file_path = line[3:]
                    status["changed_files"].append(
                        {
                            "file": file_path,
                            "status": status_code,
                            "staged": status_code[0] != " " and status_code[0] != "?",
                            "modified": status_code[1] != " ",
                        }
                    )

        # Parse ahead/behind
        if sync_result.returncode == 0:
            counts = sync_result.stdout.strip().split("\t")
            if len(counts) == 2:
                status["behind"] = int(counts[0])
                status["ahead"] = int(counts[1])

        return status

    except subprocess.TimeoutExpired:
        return {
            "valid": False,
            "error": "Git command timed out",
        }
    except Exception as e:
        return {
            "valid": False,
            "error": f"Error getting repository status: {str(e)}",
        }
