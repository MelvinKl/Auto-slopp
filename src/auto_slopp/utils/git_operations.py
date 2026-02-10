"""Git operations utilities for workers.

This module provides pure functions for common git operations
used across different workers.
"""

import logging
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class GitOperationError(Exception):
    """Exception raised when git operations fail."""

    pass


def get_local_branches(repo_dir: Path) -> List[Dict[str, Any]]:
    """Get all local branches with their last commit dates.

    Args:
        repo_dir: Path to the git repository

    Returns:
        List of dictionaries containing branch information.

    Raises:
        GitOperationError: If git command fails
    """
    try:
        result = subprocess.run(
            [
                "git",
                "branch",
                "-v",
                "--format=%(refname:short)%00%(authordate:iso-strict)%00%(objectname)",
            ],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            check=True,
        )

        branches = []
        for line in result.stdout.strip().split("\n"):
            if line.strip():
                parts = line.split("\x00")
                if len(parts) >= 3:
                    name = parts[0].strip("* ").strip()  # Remove '* ' prefix for current branch
                    date_str = parts[1]
                    try:
                        commit_date = datetime.fromisoformat(date_str)
                    except ValueError:
                        # Fallback to handling git's regular iso format
                        date_str = date_str.replace(" ", "T", 1).replace(" ", "")
                        commit_date = datetime.fromisoformat(date_str)

                    commit_hash = parts[2]

                    # Skip main/master branches by default
                    if name not in ["main", "master"]:
                        branches.append(
                            {
                                "name": name,
                                "last_commit_date": commit_date,
                                "last_commit_hash": commit_hash,
                                "days_old": (datetime.now(timezone.utc) - commit_date).days,
                            }
                        )

        return branches

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get local branches in {repo_dir}: {e}")
        raise GitOperationError(f"Failed to get local branches: {e}")


def get_remote_branches(repo_dir: Path) -> set:
    """Get all branches that exist on the remote.

    Args:
        repo_dir: Path to the git repository

    Returns:
        Set of remote branch names (without 'origin/' prefix).

    Raises:
        GitOperationError: If git command fails
    """
    try:
        result = subprocess.run(
            ["git", "branch", "-r", "--format=%(refname:short)"],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            check=True,
        )

        remote_branches = set()
        for line in result.stdout.strip().split("\n"):
            if line.strip() and "HEAD" not in line:
                # Remove 'origin/' prefix and clean up
                branch_name = line.strip().replace("origin/", "")
                if branch_name:
                    remote_branches.add(branch_name)

        return remote_branches

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get remote branches in {repo_dir}: {e}")
        raise GitOperationError(f"Failed to get remote branches: {e}")


def get_current_branch(repo_dir: Path) -> str:
    """Get the name of the current branch.

    Args:
        repo_dir: Path to the git repository

    Returns:
        Name of the current branch.

    Raises:
        GitOperationError: If git command fails
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get current branch in {repo_dir}: {e}")
        raise GitOperationError(f"Failed to get current branch: {e}")


def delete_branch(repo_dir: Path, branch_name: str) -> bool:
    """Delete a local branch.

    Args:
        repo_dir: Path to the git repository
        branch_name: Name of the branch to delete

    Returns:
        True if deletion was successful, False otherwise.
    """
    try:
        # Don't delete current branch
        current_branch = get_current_branch(repo_dir)
        if branch_name == current_branch:
            logger.warning(f"Cannot delete current branch '{branch_name}'")
            return False

        # Delete the branch
        subprocess.run(
            ["git", "branch", "-D", branch_name],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            check=True,
        )

        logger.info(f"Successfully deleted branch '{branch_name}'")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to delete branch '{branch_name}': {e}")
        return False


def has_changes(repo_dir: Path) -> bool:
    """Check if there are uncommitted changes in the repository.

    Args:
        repo_dir: Path to the git repository

    Returns:
        True if there are changes to commit, False otherwise.

    Raises:
        GitOperationError: If git command fails
    """
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            check=True,
        )
        return bool(result.stdout.strip())

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to check git status in {repo_dir}: {e}")
        raise GitOperationError(f"Failed to check git status: {e}")


def commit_and_push_changes(
    repo_dir: Path, commit_message: str, push_if_remote: bool = True
) -> Tuple[bool, Optional[bool]]:
    """Commit and push changes in a git repository.

    Args:
        repo_dir: Path to the git repository
        commit_message: Message for the commit
        push_if_remote: Whether to push if a remote exists

    Returns:
        Tuple of (commit_success, push_success). Push_success is None if no remote.

    Raises:
        GitOperationError: If git operations fail
    """
    original_cwd = os.getcwd()
    commit_success = False
    push_success = None

    try:
        # Change to repository directory
        os.chdir(repo_dir)

        # Check if this is a git repository
        if not (repo_dir / ".git").exists():
            logger.info(f"Initializing git repository in {repo_dir}")
            subprocess.run(["git", "init"], check=True, capture_output=True)

        # Add all changes
        subprocess.run(["git", "add", "."], check=True, capture_output=True)

        # Check if there are changes to commit
        if not has_changes(repo_dir):
            logger.info("No changes to commit")
            return True, None

        # Commit changes
        subprocess.run(
            ["git", "commit", "-m", commit_message],
            check=True,
            capture_output=True,
        )
        commit_success = True

        # Check if there's a remote to push to
        if push_if_remote:
            remote_result = subprocess.run(
                ["git", "remote", "-v"],
                capture_output=True,
                text=True,
                check=True,
            )

            if remote_result.stdout.strip():
                # Push changes if remote exists
                subprocess.run(["git", "push"], check=True, capture_output=True)
                logger.info(f"Committed and pushed changes: {commit_message}")
                push_success = True
            else:
                logger.info(f"Committed changes (no remote to push): {commit_message}")
                push_success = None

        return commit_success, push_success

    except subprocess.CalledProcessError as e:
        logger.error(f"Git operations failed: {e}")
        raise GitOperationError(f"Git operations failed: {e}")

    finally:
        os.chdir(original_cwd)
