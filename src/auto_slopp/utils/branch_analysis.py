"""Branch analysis utilities for stale branch cleanup.

This module provides utilities for analyzing and identifying stale branches.
"""

import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Set

from auto_slopp.utils.git_operations import (
    delete_branch,
    get_local_branches,
    get_remote_branches,
)

logger = logging.getLogger(__name__)


def create_branch_cleanup_result(repo_dir: Path) -> dict:
    """Create a result dictionary for branch cleanup.

    Args:
        repo_dir: Path to the repository directory

    Returns:
        Initialized result dictionary.
    """
    return {
        "repository": repo_dir.name,
        "path": str(repo_dir),
        "success": False,
        "branches_deleted": 0,
        "branches_failed_to_delete": 0,
        "deleted_branches": [],
        "failed_deletions": [],
        "error": None,
    }


def identify_stale_branches(
    local_branches: List[Dict[str, Any]], remote_branches: Set[str], days_threshold: int
) -> List[Dict[str, Any]]:
    """Identify branches that are stale and should be deleted.

    Args:
        local_branches: List of local branch information
        remote_branches: Set of remote branch names
        days_threshold: Days after which a branch is considered stale

    Returns:
        List of stale branch information.
    """
    stale_branches = []
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_threshold)

    for branch in local_branches:
        branch_name = branch["name"]

        # Check if branch not on remote and is older than threshold
        if branch_name not in remote_branches and branch["last_commit_date"] < cutoff_date:
            stale_branches.append(branch)

    logger.info(f"Found {len(stale_branches)} stale branches out of {len(local_branches)} local branches")
    return stale_branches


def delete_stale_branches(
    stale_branches: List[Dict[str, Any]], repo_dir: Path, dry_run: bool = False
) -> tuple[list, list]:
    """Delete stale branches.

    Args:
        stale_branches: List of stale branch information
        repo_dir: Path to the repository directory
        dry_run: If True, only report deletions without actually deleting

    Returns:
        Tuple of (deleted_branches, failed_deletions)
    """
    deleted_branches = []
    failed_deletions = []

    for branch_info in stale_branches:
        branch_name = branch_info["name"]

        if dry_run:
            logger.info(
                f"DRY RUN: Would delete branch '{branch_name}' "
                f"(last commit: {branch_info['last_commit_date']}) in {repo_dir.name}"
            )
            deleted_branches.append(branch_info)
        else:
            if delete_branch(repo_dir, branch_name):
                deleted_branches.append(branch_info)
            else:
                failed_deletions.append(branch_info)

    return deleted_branches, failed_deletions


def analyze_repository_branches(repo_dir: Path, days_threshold: int, dry_run: bool = False) -> dict:
    """Analyze branches in a repository and identify stale ones.

    Args:
        repo_dir: Path to the repository directory
        days_threshold: Days after which a branch is considered stale
        dry_run: If True, only report what would be deleted

    Returns:
        Dictionary containing branch analysis results.
    """
    import os

    result = create_branch_cleanup_result(repo_dir)

    try:
        original_cwd = os.getcwd()
    except OSError:
        # If we can't get current directory, use repo_dir as fallback
        original_cwd = str(repo_dir)

    try:
        # Change to repository directory
        os.chdir(repo_dir)

        # Get all branches information
        local_branches = get_local_branches(repo_dir)
        remote_branches = get_remote_branches(repo_dir)

        # Find stale branches
        stale_branches = identify_stale_branches(local_branches, remote_branches, days_threshold)

        # Delete stale branches (or simulate deletion for dry run)
        deleted_branches, failed_deletions = delete_stale_branches(stale_branches, repo_dir, dry_run)

        # Update result
        result.update(
            {
                "success": True,
                "branches_deleted": len(deleted_branches),
                "branches_failed_to_delete": len(failed_deletions),
                "deleted_branches": deleted_branches,
                "failed_deletions": failed_deletions,
                "total_local_branches": len(local_branches),
                "total_remote_branches": len(remote_branches),
                "stale_branches_found": len(stale_branches),
            }
        )

        logger.info(
            f"Completed stale branch cleanup for {repo_dir.name}: "
            f"{len(deleted_branches)} deleted, {len(failed_deletions)} failed"
        )

        return result

    except Exception as e:
        # Restore working directory on error
        try:
            os.chdir(original_cwd)
        except OSError:
            pass

        logger.error(f"Stale branch cleanup failed for {repo_dir.name}: {str(e)}")
        result["error"] = str(e)
        return result

    finally:
        # Restore working directory
        try:
            os.chdir(original_cwd)
        except OSError:
            pass
