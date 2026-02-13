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

from auto_slopp.utils.opencode import run_opencode

logger = logging.getLogger(__name__)


class GitOperationError(Exception):
    """Exception raised when git operations fail."""

    pass


def _handle_git_operation_failure(
    operation: str,
    repo_dir: Path,
    error_message: str,
    timeout: int = 300,
) -> None:
    """Handle git operation failure by calling OpenCode to fix the issue.

    Args:
        operation: The name of the git operation that failed
        repo_dir: Path to the git repository
        error_message: The error message from the failed operation
        timeout: Timeout for OpenCode execution in seconds
    """
    logger.warning(f"Git operation '{operation}' failed in {repo_dir.name}: {error_message}")
    logger.info(f"Calling OpenCode to fix the failed git operation: {operation}")

    instructions = (
        f"Fix the failed git operation '{operation}' in the repository at {repo_dir}. "
        f"The error was: {error_message}. "
        f"Please resolve the issue and ensure the git operation completes successfully."
    )

    try:
        result = run_opencode(
            additional_instructions=instructions,
            working_directory=repo_dir,
            timeout=timeout,
            capture_output=True,
        )

        if result.get("success"):
            logger.info(f"OpenCode successfully resolved the git operation '{operation}' failure")
        else:
            logger.error(
                f"OpenCode failed to resolve git operation '{operation}' failure: {result.get('error', 'Unknown error')}"
            )
    except Exception as e:
        logger.error(f"Failed to call OpenCode for git operation '{operation}' failure: {str(e)}")


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
        # Check both stdout and stderr for error messages
        error_output = (e.stderr.strip() or e.stdout.strip()) if e.stderr or e.stdout else str(e)
        error_msg = f"Failed to get local branches: {error_output}"
        logger.error(f"Failed to get local branches in {repo_dir}: {error_output}")
        _handle_git_operation_failure("get_local_branches", repo_dir, error_msg)
        raise GitOperationError(error_msg)


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
        # Check both stdout and stderr for error messages
        error_output = (e.stderr.strip() or e.stdout.strip()) if e.stderr or e.stdout else str(e)
        error_msg = f"Failed to get remote branches: {error_output}"
        logger.error(f"Failed to get remote branches in {repo_dir}: {error_output}")
        _handle_git_operation_failure("get_remote_branches", repo_dir, error_msg)
        raise GitOperationError(error_msg)


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
        # Check both stdout and stderr for error messages
        error_output = (e.stderr.strip() or e.stdout.strip()) if e.stderr or e.stdout else str(e)
        error_msg = f"Failed to get current branch: {error_output}"
        logger.error(f"Failed to get current branch in {repo_dir}: {error_output}")
        _handle_git_operation_failure("get_current_branch", repo_dir, error_msg)
        raise GitOperationError(error_msg)


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
        # Check both stdout and stderr for error messages
        error_output = (e.stderr.strip() or e.stdout.strip()) if e.stderr or e.stdout else str(e)
        error_msg = f"Failed to delete branch '{branch_name}': {error_output}"
        logger.error(f"Failed to delete branch '{branch_name}': {error_output}")
        _handle_git_operation_failure("delete_branch", repo_dir, error_msg)
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
        # Check both stdout and stderr for error messages
        error_output = (e.stderr.strip() or e.stdout.strip()) if e.stderr or e.stdout else str(e)
        error_msg = f"Failed to check git status: {error_output}"
        logger.error(f"Failed to check git status in {repo_dir}: {error_output}")
        _handle_git_operation_failure("has_changes", repo_dir, error_msg)
        raise GitOperationError(error_msg)


def has_remote(repo_dir: Path, remote_name: str = "origin") -> bool:
    """Check if a remote exists in the repository.

    Args:
        repo_dir: Path to the git repository
        remote_name: Name of the remote to check (default: "origin")

    Returns:
        True if the remote exists, False otherwise.
    """
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", remote_name],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            check=True,
        )
        return bool(result.stdout.strip())
    except subprocess.CalledProcessError:
        return False


def checkout_branch_resilient(repo_dir: Path, branch: str, fetch_first: bool = True, timeout: int = 60) -> bool:
    """Checkout a git branch with enhanced resilience.

    If checkout fails, performs a git reset --hard and retries.

    Args:
        repo_dir: Path to the git repository
        branch: Branch name to checkout
        fetch_first: Whether to fetch from remote before checkout
        timeout: Timeout for individual git commands in seconds

    Returns:
        True if checkout successful, False otherwise
    """
    try:
        logger.info(f"Checking out branch '{branch}' in {repo_dir.name}")

        # Fetch latest changes if requested
        if fetch_first and has_remote(repo_dir, "origin"):
            logger.debug(f"Fetching latest changes for {repo_dir.name}")
            fetch_result = subprocess.run(
                ["git", "fetch", "origin"],
                cwd=repo_dir,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            if fetch_result.returncode != 0:
                # Check both stdout and stderr for error messages (git can output to either)
                fetch_error = fetch_result.stderr.strip() or fetch_result.stdout.strip()
                logger.warning(f"Fetch failed for {repo_dir.name}: {fetch_error}")
                # Continue with checkout even if fetch fails

        # First attempt to checkout
        checkout_result = subprocess.run(
            ["git", "checkout", branch],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        if checkout_result.returncode == 0:
            logger.info(f"Successfully checked out '{branch}' in {repo_dir.name}")

            # Pull latest changes for the branch only if remote exists
            if has_remote(repo_dir, "origin"):
                pull_result = subprocess.run(
                    ["git", "pull", "--rebase=false", "origin", branch],
                    cwd=repo_dir,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                )
                if pull_result.returncode != 0:
                    # Check both stdout and stderr for error messages
                    pull_error = pull_result.stderr.strip() or pull_result.stdout.strip()
                    logger.warning(f"Pull failed for branch '{branch}' in {repo_dir.name}: {pull_error}")
                    # Don't fail the checkout if pull fails

            return True

        # If first checkout attempt failed, try reset and retry
        # Check both stdout and stderr for error messages
        checkout_error = checkout_result.stderr.strip() or checkout_result.stdout.strip()
        logger.warning(f"Initial checkout failed for '{branch}' in {repo_dir.name}: {checkout_error}")
        logger.info(f"Attempting git reset --hard and retry for '{branch}' in {repo_dir.name}")

        # Reset to clean state
        reset_result = subprocess.run(
            ["git", "reset", "--hard"],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if reset_result.returncode != 0:
            # Check both stdout and stderr for error messages
            reset_error = reset_result.stderr.strip() or reset_result.stdout.strip()
            error_msg = f"Git reset --hard failed: {reset_error}"
            logger.error(f"Git reset --hard failed in {repo_dir.name}: {reset_error}")
            _handle_git_operation_failure("checkout_branch_resilient", repo_dir, error_msg)
            return False

        # Clean untracked files
        clean_result = subprocess.run(
            ["git", "clean", "-fd"],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if clean_result.returncode != 0:
            # Check both stdout and stderr for error messages
            clean_error = clean_result.stderr.strip() or clean_result.stdout.strip()
            logger.warning(f"Git clean failed in {repo_dir.name}: {clean_error}")
            # Continue despite clean failure

        # Second attempt to checkout after reset
        retry_checkout_result = subprocess.run(
            ["git", "checkout", branch],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        if retry_checkout_result.returncode == 0:
            logger.info(f"Successfully checked out '{branch}' in {repo_dir.name} after reset")

            # Pull latest changes for the branch only if remote exists
            if has_remote(repo_dir, "origin"):
                pull_result = subprocess.run(
                    ["git", "pull", "--rebase=false", "origin", branch],
                    cwd=repo_dir,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                )
                if pull_result.returncode != 0:
                    # Check both stdout and stderr for error messages
                    pull_error = pull_result.stderr.strip() or pull_result.stdout.strip()
                    logger.warning(f"Pull failed for branch '{branch}' in {repo_dir.name}: {pull_error}")

            return True
        else:
            # Check both stdout and stderr for error messages
            retry_error = retry_checkout_result.stderr.strip() or retry_checkout_result.stdout.strip()
            error_msg = f"Failed to checkout '{branch}' even after reset: {retry_error}"
            logger.error(f"Failed to checkout '{branch}' in {repo_dir.name} even after reset: {retry_error}")
            _handle_git_operation_failure("checkout_branch_resilient", repo_dir, error_msg)
            return False

    except subprocess.TimeoutExpired:
        error_msg = f"Timeout checking out '{branch}'"
        logger.error(f"Timeout checking out '{branch}' in {repo_dir.name}")
        _handle_git_operation_failure("checkout_branch_resilient", repo_dir, error_msg)
        return False
    except Exception as e:
        error_msg = f"Error checking out '{branch}': {str(e)}"
        logger.error(f"Error checking out '{branch}' in {repo_dir.name}: {str(e)}")
        _handle_git_operation_failure("checkout_branch_resilient", repo_dir, error_msg)
        return False


def push_branch(repo_dir: Path, branch: str, force: bool = True, timeout: int = 60) -> bool:
    """Push a branch to the remote repository.

    Args:
        repo_dir: Path to the git repository
        branch: Branch name to push
        force: Whether to force push
        timeout: Timeout for git command in seconds

    Returns:
        True if push successful, False otherwise.

    Raises:
        GitOperationError: If git command fails
    """
    if not has_remote(repo_dir, "origin"):
        logger.warning(f"No remote 'origin' found in {repo_dir.name}, cannot push branch '{branch}'")
        return False

    try:
        cmd = ["git", "push", "origin", branch]
        if force:
            cmd.append("--force")

        result = subprocess.run(
            cmd,
            cwd=repo_dir,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        if result.returncode != 0:
            # Check both stdout and stderr for error messages
            push_error = result.stderr.strip() or result.stdout.strip()
            error_msg = f"Failed to push branch '{branch}': {push_error}"
            logger.error(f"Failed to push branch '{branch}' in {repo_dir.name}: {push_error}")
            _handle_git_operation_failure("push_branch", repo_dir, error_msg)
            return False

        logger.info(f"Successfully pushed branch '{branch}' to origin")
        return True

    except subprocess.TimeoutExpired:
        error_msg = f"Timeout pushing branch '{branch}'"
        logger.error(f"Timeout pushing branch '{branch}' in {repo_dir.name}")
        _handle_git_operation_failure("push_branch", repo_dir, error_msg)
        return False
    except subprocess.CalledProcessError as e:
        # Check both stdout and stderr for error messages
        error_output = (e.stderr.strip() or e.stdout.strip()) if e.stderr or e.stdout else str(e)
        error_msg = f"Failed to push branch '{branch}': {error_output}"
        logger.error(f"Failed to push branch '{branch}' in {repo_dir.name}: {error_output}")
        _handle_git_operation_failure("push_branch", repo_dir, error_msg)
        return False


def merge_main_into_branch(
    repo_dir: Path, branch: str, remote_name: str = "origin", timeout: int = 60
) -> Tuple[bool, str]:
    """Merge origin/main into the current branch.

    Args:
        repo_dir: Path to the git repository
        branch: Branch name to merge into
        remote_name: Name of the remote (default: origin)
        timeout: Timeout for git commands in seconds

    Returns:
        Tuple of (success, message). If success is False, message contains error details.

    Raises:
        GitOperationError: If git operations fail
    """
    if not has_remote(repo_dir, remote_name):
        error_msg = f"No remote '{remote_name}' found in {repo_dir.name}"
        logger.warning(error_msg)
        return False, error_msg

    try:
        # Fetch the main branch from remote
        fetch_result = subprocess.run(
            ["git", "fetch", remote_name, "main:main"],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if fetch_result.returncode != 0:
            fetch_error = fetch_result.stderr.strip() or fetch_result.stdout.strip()
            error_msg = f"Failed to fetch main: {fetch_error}"
            logger.error(f"Failed to fetch main in {repo_dir.name}: {fetch_error}")
            _handle_git_operation_failure("merge_main_into_branch", repo_dir, error_msg)
            return False, fetch_error

        # Merge origin/main into current branch
        merge_result = subprocess.run(
            ["git", "merge", f"{remote_name}/main", "--no-edit"],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if merge_result.returncode != 0:
            merge_error = merge_result.stderr.strip() or merge_result.stdout.strip()
            logger.warning(f"Merge had conflicts or failed: {merge_error}")

            # Abort the merge
            abort_result = subprocess.run(
                ["git", "merge", "--abort"],
                cwd=repo_dir,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            if abort_result.returncode != 0:
                abort_error = abort_result.stderr.strip() or abort_result.stdout.strip()
                logger.error(f"Failed to abort merge: {abort_error}")

            return False, merge_error

        logger.info(f"Successfully merged {remote_name}/main into branch '{branch}'")
        return True, "Merge successful"

    except subprocess.TimeoutExpired:
        error_msg = f"Timeout during merge operation for branch '{branch}'"
        logger.error(f"Timeout merging main into branch '{branch}' in {repo_dir.name}")
        _handle_git_operation_failure("merge_main_into_branch", repo_dir, error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"Error merging main into branch '{branch}': {str(e)}"
        logger.error(f"Error merging main into branch '{branch}' in {repo_dir.name}: {str(e)}")
        _handle_git_operation_failure("merge_main_into_branch", repo_dir, error_msg)
        return False, error_msg


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
        # Check both stdout and stderr for error messages
        error_output = (e.stderr.strip() or e.stdout.strip()) if e.stderr or e.stdout else str(e)
        error_msg = f"Git operations failed: {error_output}"
        logger.error(f"Git operations failed: {error_output}")
        _handle_git_operation_failure("commit_and_push_changes", repo_dir, error_msg)
        raise GitOperationError(error_msg)

    finally:
        os.chdir(original_cwd)
