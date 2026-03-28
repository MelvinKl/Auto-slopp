"""Git helper utilities for committing changes.

This module provides a simple interface for committing changes
in the auto-slopp workflow.
"""

import logging
from pathlib import Path
from typing import Optional, Tuple

from auto_slopp.utils.git_operations import commit_and_push_changes

logger = logging.getLogger(__name__)


def commit(repo_path: Path, message: str, push_if_remote: bool = False) -> Tuple[bool, Optional[bool]]:
    """Commit changes in the repository.

    Args:
        repo_path: Path to the git repository
        message: Commit message
        push_if_remote: Whether to push if a remote exists

    Returns:
        Tuple of (commit_success, push_success). Push_success is None if no remote.
    """
    logger.info(f"Committing changes: {message}")
    return commit_and_push_changes(repo_path, message, push_if_remote)


def commit_and_push(repo_path: Path, message: str) -> Tuple[bool, bool]:
    """Commit and push changes in the repository.

    Args:
        repo_path: Path to the git repository
        message: Commit message

    Returns:
        Tuple of (commit_success, push_success)
    """
    logger.info(f"Committing and pushing changes: {message}")
    return commit_and_push_changes(repo_path, message, push_if_remote=True)
