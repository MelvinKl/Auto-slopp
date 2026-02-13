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


def _run_git_command(
    repo_dir: Path,
    *args: str,
    check: bool = True,
    timeout: int = 60,
    capture_output: bool = True,
) -> subprocess.CompletedProcess:
    """Run a git command in the specified repository.

    Args:
        repo_dir: Path to the git repository
        *args: Git command arguments
        check: Whether to raise exception on non-zero return code
        timeout: Timeout for the command in seconds
        capture_output: Whether to capture output

    Returns:
        CompletedProcess instance

    Raises:
        GitOperationError: If git command fails and check is True
    """
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=repo_dir,
            capture_output=capture_output,
            text=capture_output,
            check=check,
            timeout=timeout,
        )
        return result
    except subprocess.CalledProcessError as e:
        error_output = (e.stderr.strip() or e.stdout.strip()) if e.stderr or e.stdout else str(e)
        logger.error(f"Git command 'git {' '.join(args)}' failed in {repo_dir}: {error_output}")
        raise GitOperationError(f"Git command failed: {error_output}")
    except (subprocess.TimeoutExpired, TimeoutError) as e:
        logger.error(f"Git command 'git {' '.join(args)}' timed out in {repo_dir}")
        raise GitOperationError(f"Git command timed out: {e}")


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
    result = _run_git_command(
        repo_dir,
        "branch",
        "-v",
        "--format=%(refname:short)%00%(authordate:iso-strict)%00%(objectname)",
    )

    branches = []
    for line in result.stdout.strip().split("\n"):
        if line.strip():
            parts = line.split("\x00")
            if len(parts) >= 3:
                name = parts[0].strip("* ").strip()
                date_str = parts[1]
                try:
                    commit_date = datetime.fromisoformat(date_str)
                except ValueError:
                    date_str = date_str.replace(" ", "T", 1).replace(" ", "")
                    commit_date = datetime.fromisoformat(date_str)

                commit_hash = parts[2]

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


def get_remote_branches(repo_dir: Path) -> set:
    """Get all branches that exist on the remote.

    Args:
        repo_dir: Path to the git repository

    Returns:
        Set of remote branch names (without 'origin/' prefix).

    Raises:
        GitOperationError: If git command fails
    """
    result = _run_git_command(repo_dir, "branch", "-r", "--format=%(refname:short)")

    remote_branches = set()
    for line in result.stdout.strip().split("\n"):
        if line.strip() and "HEAD" not in line:
            branch_name = line.strip().replace("origin/", "")
            if branch_name:
                remote_branches.add(branch_name)

    return remote_branches


def get_current_branch(repo_dir: Path) -> str:
    """Get the name of the current branch.

    Args:
        repo_dir: Path to the git repository

    Returns:
        Name of the current branch.

    Raises:
        GitOperationError: If git command fails
    """
    result = _run_git_command(repo_dir, "rev-parse", "--abbrev-ref", "HEAD")
    return result.stdout.strip()


def delete_branch(repo_dir: Path, branch_name: str) -> bool:
    """Delete a local branch.

    Args:
        repo_dir: Path to the git repository
        branch_name: Name of the branch to delete

    Returns:
        True if deletion was successful, False otherwise.
    """
    current_branch = get_current_branch(repo_dir)
    if branch_name == current_branch:
        logger.warning(f"Cannot delete current branch '{branch_name}'")
        return False

    try:
        _run_git_command(repo_dir, "branch", "-D", branch_name)
        logger.info(f"Successfully deleted branch '{branch_name}'")
        return True
    except GitOperationError as e:
        logger.error(f"Failed to delete branch '{branch_name}': {e}")
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
    result = _run_git_command(repo_dir, "status", "--porcelain")
    return bool(result.stdout.strip())


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

        if fetch_first:
            logger.debug(f"Fetching latest changes for {repo_dir.name}")
            fetch_result = _run_git_command(repo_dir, "fetch", "origin", check=False, timeout=timeout)
            if fetch_result.returncode != 0:
                fetch_error = fetch_result.stderr.strip() or fetch_result.stdout.strip()
                logger.warning(f"Fetch failed for {repo_dir.name}: {fetch_error}")

        checkout_result = _run_git_command(repo_dir, "checkout", branch, check=False, timeout=timeout)

        if checkout_result.returncode == 0:
            logger.info(f"Successfully checked out '{branch}' in {repo_dir.name}")

            pull_result = _run_git_command(
                repo_dir,
                "pull",
                "--rebase=false",
                "origin",
                branch,
                check=False,
                timeout=timeout,
            )
            if pull_result.returncode != 0:
                pull_error = pull_result.stderr.strip() or pull_result.stdout.strip()
                logger.warning(f"Pull failed for branch '{branch}' in {repo_dir.name}: {pull_error}")

            return True

        checkout_error = checkout_result.stderr.strip() or checkout_result.stdout.strip()
        logger.warning(f"Initial checkout failed for '{branch}' in {repo_dir.name}: {checkout_error}")
        logger.info(f"Attempting git reset --hard and retry for '{branch}' in {repo_dir.name}")

        reset_result = _run_git_command(repo_dir, "reset", "--hard", check=False, timeout=timeout)
        if reset_result.returncode != 0:
            reset_error = reset_result.stderr.strip() or reset_result.stdout.strip()
            error_msg = f"Git reset --hard failed: {reset_error}"
            logger.error(f"Git reset --hard failed in {repo_dir.name}: {reset_error}")
            _handle_git_operation_failure("checkout_branch_resilient", repo_dir, error_msg)
            return False

        clean_result = _run_git_command(repo_dir, "clean", "-fd", check=False, timeout=timeout)
        if clean_result.returncode != 0:
            clean_error = clean_result.stderr.strip() or clean_result.stdout.strip()
            logger.warning(f"Git clean failed in {repo_dir.name}: {clean_error}")

        retry_checkout_result = _run_git_command(repo_dir, "checkout", branch, check=False, timeout=timeout)

        if retry_checkout_result.returncode == 0:
            logger.info(f"Successfully checked out '{branch}' in {repo_dir.name} after reset")

            pull_result = _run_git_command(
                repo_dir,
                "pull",
                "--rebase=false",
                "origin",
                branch,
                check=False,
                timeout=timeout,
            )
            if pull_result.returncode != 0:
                pull_error = pull_result.stderr.strip() or pull_result.stdout.strip()
                logger.warning(f"Pull failed for branch '{branch}' in {repo_dir.name}: {pull_error}")

            return True
        else:
            retry_error = retry_checkout_result.stderr.strip() or retry_checkout_result.stdout.strip()
            error_msg = f"Failed to checkout '{branch}' even after reset: {retry_error}"
            logger.error(f"Failed to checkout '{branch}' in {repo_dir.name} even after reset: {retry_error}")
            _handle_git_operation_failure("checkout_branch_resilient", repo_dir, error_msg)
            return False

    except GitOperationError as e:
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
    cmd = ["push", "origin", branch]
    if force:
        cmd.append("--force")

    result = _run_git_command(repo_dir, *cmd, check=False, timeout=timeout)

    if result.returncode != 0:
        push_error = result.stderr.strip() or result.stdout.strip()
        error_msg = f"Failed to push branch '{branch}': {push_error}"
        logger.error(f"Failed to push branch '{branch}' in {repo_dir.name}: {push_error}")
        _handle_git_operation_failure("push_branch", repo_dir, error_msg)
        return False

    logger.info(f"Successfully pushed branch '{branch}' to origin")
    return True


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
    try:
        fetch_result = _run_git_command(repo_dir, "fetch", remote_name, "main:main", check=False, timeout=timeout)
        if fetch_result.returncode != 0:
            fetch_error = fetch_result.stderr.strip() or fetch_result.stdout.strip()
            error_msg = f"Failed to fetch main: {fetch_error}"
            logger.error(f"Failed to fetch main in {repo_dir.name}: {fetch_error}")
            _handle_git_operation_failure("merge_main_into_branch", repo_dir, error_msg)
            return False, fetch_error

        merge_result = _run_git_command(
            repo_dir,
            "merge",
            f"{remote_name}/main",
            "--no-edit",
            check=False,
            timeout=timeout,
        )
        if merge_result.returncode != 0:
            merge_error = merge_result.stderr.strip() or merge_result.stdout.strip()
            logger.warning(f"Merge had conflicts or failed: {merge_error}")

            if "CONFLICT" in merge_error:
                logger.info("Merge conflict detected, calling OpenCode to resolve")
                _handle_git_operation_failure("merge_main_into_branch", repo_dir, merge_error)
                return (
                    False,
                    f"Merge conflict detected and OpenCode attempted resolution: {merge_error}",
                )

            abort_result = _run_git_command(repo_dir, "merge", "--abort", check=False, timeout=timeout)
            if abort_result.returncode != 0:
                abort_error = abort_result.stderr.strip() or abort_result.stdout.strip()
                logger.error(f"Failed to abort merge: {abort_error}")

            return False, merge_error

        logger.info(f"Successfully merged {remote_name}/main into branch '{branch}'")
        return True, "Merge successful"

    except GitOperationError as e:
        error_msg = f"Error merging main into branch '{branch}': {str(e)}"
        logger.error(f"Error merging main into branch '{branch}' in {repo_dir.name}: {str(e)}")
        _handle_git_operation_failure("merge_main_into_branch", repo_dir, error_msg)
        return False, error_msg


def is_bare_repository(repo_dir: Path) -> bool:
    """Check if a repository is a bare repository.

    Args:
        repo_dir: Path to the git repository

    Returns:
        True if the repository is bare, False otherwise.
    """
    result = _run_git_command(repo_dir, "rev-parse", "--is-bare-repository", check=False)
    return result.stdout.strip() == "true"


def get_remotes(repo_dir: Path) -> List[Dict[str, str]]:
    """Get all remotes with their URLs.

    Args:
        repo_dir: Path to the git repository

    Returns:
        List of dictionaries containing remote name and URL.
    """
    result = _run_git_command(repo_dir, "remote", "-v", check=False)

    if result.returncode != 0:
        return []

    remotes = []
    for line in result.stdout.strip().split("\n"):
        if line.strip():
            parts = line.split("\t")
            if len(parts) >= 2:
                remote_name = parts[0]
                url_part = parts[1].split(" ")[0]
                remotes.append({"name": remote_name, "url": url_part})

    return remotes


def get_default_branch(repo_dir: Path) -> Optional[str]:
    """Get the default branch of the repository.

    Args:
        repo_dir: Path to the git repository

    Returns:
        Name of the default branch, or None if not found.
    """
    result = _run_git_command(repo_dir, "config", "--get", "init.defaultBranch", check=False)

    if result.returncode == 0:
        return result.stdout.strip()

    for branch in ["main", "master", "develop"]:
        branch_result = _run_git_command(repo_dir, "rev-parse", "--verify", branch, check=False)
        if branch_result.returncode == 0:
            return branch

    return None


def branch_exists(repo_dir: Path, branch: str) -> bool:
    """Check if a branch exists in the repository.

    Args:
        repo_dir: Path to the git repository
        branch: Branch name to check

    Returns:
        True if the branch exists, False otherwise.
    """
    result = _run_git_command(repo_dir, "rev-parse", "--verify", branch, check=False)
    return result.returncode == 0


def get_ahead_behind(repo_dir: Path, remote: str = "origin", branch: Optional[str] = None) -> Tuple[int, int]:
    """Get ahead/behind count between local and remote branch.

    Args:
        repo_dir: Path to the git repository
        remote: Remote name (default: origin)
        branch: Branch name (default: current branch)

    Returns:
        Tuple of (behind, ahead) counts.
    """
    if branch is None:
        branch = get_current_branch(repo_dir)

    try:
        result = _run_git_command(
            repo_dir,
            "rev-list",
            "--count",
            "--left-right",
            f"HEAD...{remote}/{branch}",
            check=False,
        )

        if result.returncode == 0:
            counts = result.stdout.strip().split("\t")
            if len(counts) == 2:
                return int(counts[0]), int(counts[1])

    except Exception:
        pass

    return 0, 0


def pull_from_remote(repo_dir: Path, remote: str = "origin", branch: str = "main") -> Tuple[bool, str]:
    """Pull changes from a remote branch.

    Args:
        repo_dir: Path to the git repository
        remote: Remote name (default: origin)
        branch: Branch name (default: main)

    Returns:
        Tuple of (success, message).
    """
    result = _run_git_command(repo_dir, "pull", remote, branch, check=False)

    if result.returncode == 0:
        return True, "Pull successful"

    error_msg = result.stderr.strip() or result.stdout.strip()
    return False, error_msg


def push_to_remote(repo_dir: Path, remote: str = "origin", branch: Optional[str] = None) -> Tuple[bool, str]:
    """Push changes to a remote branch.

    Args:
        repo_dir: Path to the git repository
        remote: Remote name (default: origin)
        branch: Branch name (default: current branch)

    Returns:
        Tuple of (success, message).
    """
    if branch is None:
        branch = get_current_branch(repo_dir)

    result = _run_git_command(repo_dir, "push", remote, branch, check=False)

    if result.returncode == 0:
        return True, "Push successful"

    error_msg = result.stderr.strip() or result.stdout.strip()
    return False, error_msg


def is_git_repo(directory: Path) -> bool:
    """Check if a directory is inside a git repository.

    Uses git rev-parse to detect if the directory is inside a git repo,
    which works even when the directory is a subdirectory of the repo.

    Args:
        directory: Path to check

    Returns:
        True if the directory is inside a git repository, False otherwise.
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=directory,
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
    except Exception:
        return False


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
        os.chdir(repo_dir)

        if not is_git_repo(repo_dir):
            logger.info(f"Initializing git repository in {repo_dir}")
            _run_git_command(repo_dir, "init")

        _run_git_command(repo_dir, "add", ".")

        if not has_changes(repo_dir):
            logger.info("No changes to commit")
            return True, None

        _run_git_command(repo_dir, "commit", "-m", commit_message)
        commit_success = True

        if push_if_remote:
            remote_result = _run_git_command(repo_dir, "remote", "-v")

            if remote_result.stdout.strip():
                _run_git_command(repo_dir, "push")
                logger.info(f"Committed and pushed changes: {commit_message}")
                push_success = True
            else:
                logger.info(f"Committed changes (no remote to push): {commit_message}")
                push_success = None

        return commit_success, push_success

    except GitOperationError as e:
        error_msg = f"Git operations failed: {str(e)}"
        logger.error(f"Git operations failed: {str(e)}")
        _handle_git_operation_failure("commit_and_push_changes", repo_dir, error_msg)
        raise GitOperationError(error_msg)

    finally:
        os.chdir(original_cwd)


def commit_all_changes(repo_dir: Path, commit_message: str) -> Tuple[bool, str]:
    """Commit all changes in a git repository.

    Args:
        repo_dir: Path to the git repository
        commit_message: Message for the commit

    Returns:
        Tuple of (success, message).
    """
    try:
        if not is_git_repo(repo_dir):
            return False, f"Directory is not a git repository: {repo_dir}"

        if not has_changes(repo_dir):
            return True, "No changes to commit"

        _run_git_command(repo_dir, "add", ".")
        _run_git_command(repo_dir, "commit", "-m", commit_message)
        return True, "Commit successful"

    except GitOperationError as e:
        error_msg = str(e)
        return False, f"Commit failed: {error_msg}"


def pull_from_remote(repo_dir: Path, remote: str = "origin", branch: str = "main") -> Tuple[bool, str]:
    """Pull changes from a remote branch.

    Args:
        repo_dir: Path to the git repository
        remote: Remote name (default: origin)
        branch: Branch name (default: main)

    Returns:
        Tuple of (success, message).
    """
    result = _run_git_command(repo_dir, "pull", remote, branch, check=False)

    if result.returncode == 0:
        return True, "Pull successful"

    error_msg = result.stderr.strip() or result.stdout.strip()
    return False, error_msg


def push_to_remote(repo_dir: Path, remote: str = "origin", branch: Optional[str] = None) -> Tuple[bool, str]:
    """Push changes to a remote branch.

    Args:
        repo_dir: Path to the git repository
        remote: Remote name (default: origin)
        branch: Branch name (default: current branch)

    Returns:
        Tuple of (success, message).
    """
    if branch is None:
        branch = get_current_branch(repo_dir)

    result = _run_git_command(repo_dir, "push", remote, branch, check=False)

    if result.returncode == 0:
        return True, "Push successful"

    error_msg = result.stderr.strip() or result.stdout.strip()
    return False, error_msg
