"""GitHub operations utilities for workers.

This module provides pure functions for common GitHub operations
used across different workers.
"""

import json
import logging
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import dotenv_values

from src.settings.main import settings

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
    env = os.environ.copy()
    if settings.additional_env_file and settings.additional_env_file.exists():
        env.update(dotenv_values(settings.additional_env_file))

    try:
        result = subprocess.run(
            ["gh", *args],
            cwd=repo_dir,
            capture_output=capture_output,
            text=capture_output,
            check=check,
            timeout=timeout,
            env=env,
        )
        return result
    except subprocess.CalledProcessError as e:
        error_output = (e.stderr.strip() or e.stdout.strip()) if e.stderr or e.stdout else str(e)
        logger.error(f"GitHub command 'gh {' '.join(args)}' failed in {repo_dir}: {error_output}")
        raise GitHubOperationError(f"GitHub command failed: {error_output}")
    except (subprocess.TimeoutExpired, TimeoutError) as e:
        logger.error(f"GitHub command 'gh {' '.join(args)}' timed out in {repo_dir}")
        raise GitHubOperationError(f"GitHub command timed out: {e}")


def get_open_issues(repo_dir: Path) -> List[Dict[str, Any]]:
    """Get list of open issues in the repository.

    Args:
        repo_dir: Path to the git repository

    Returns:
        List of dictionaries containing issue information (number, title, body, url).

    Raises:
        GitHubOperationError: If gh command fails
    """
    try:
        result = _run_gh_command(
            repo_dir,
            "issue",
            "list",
            "--state=open",
            "--json=number,title,body,url,author,labels",
            check=False,
        )

        if result.returncode != 0:
            issue_error = result.stderr.strip() or result.stdout.strip()
            if "Could not resolve to a Repository" in issue_error:
                logger.warning(
                    f"Cannot access repository {repo_dir.name}: likely permission denied or repository not found. "
                    f"Verify the GitHub token has access to this repository."
                )
            else:
                logger.error(f"Failed to list issues in {repo_dir.name}: {issue_error}")
            return []

        issues = json.loads(result.stdout)
        return issues

    except GitHubOperationError as e:
        logger.error(f"Error getting issues from {repo_dir.name}: {str(e)}")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse issue list JSON from {repo_dir.name}: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error getting issues from {repo_dir.name}: {str(e)}")
        return []


def get_issue_comments(repo_dir: Path, issue_number: int) -> List[Dict[str, Any]]:
    """Get list of comments on an issue in the repository.

    Args:
        repo_dir: Path to the git repository
        issue_number: Issue number to get comments for

    Returns:
        List of dictionaries containing comment information (body, author, createdAt).

    Raises:
        GitHubOperationError: If gh command fails
    """
    try:
        result = _run_gh_command(
            repo_dir,
            "issue",
            "view",
            str(issue_number),
            "--json=comments",
            check=False,
        )

        if result.returncode != 0:
            comment_error = result.stderr.strip() or result.stdout.strip()
            logger.error(f"Failed to get comments for issue #{issue_number} in {repo_dir.name}: {comment_error}")
            return []

        data = json.loads(result.stdout)
        # Extract comments from the issue view response
        raw_comments = data.get("comments", [])

        # Transform to expected format
        comments = []
        for comment in raw_comments:
            comments.append(
                {
                    "body": comment.get("body", ""),
                    "author": comment.get("author", {}).get("login") if comment.get("author") else None,
                    "createdAt": comment.get("createdAt"),
                }
            )

        return comments

    except GitHubOperationError as e:
        logger.error(f"Error getting comments for issue #{issue_number} from {repo_dir.name}: {str(e)}")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse comment JSON for issue #{issue_number} from {repo_dir.name}: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error getting comments for issue #{issue_number} from {repo_dir.name}: {str(e)}")
        return []


def close_issue(repo_dir: Path, issue_number: int) -> bool:
    """Close an issue in the repository.

    Args:
        repo_dir: Path to the git repository
        issue_number: Issue number to close

    Returns:
        True if successful, False otherwise.
    """
    try:
        result = _run_gh_command(
            repo_dir,
            "issue",
            "close",
            str(issue_number),
            check=False,
        )
        return result.returncode == 0

    except GitHubOperationError as e:
        logger.error(f"Error closing issue #{issue_number} in {repo_dir.name}: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error closing issue #{issue_number} in {repo_dir.name}: {str(e)}")
        return False


def comment_on_issue(repo_dir: Path, issue_number: int, comment: str) -> bool:
    """Add a comment to an issue in the repository.

    Args:
        repo_dir: Path to the git repository
        issue_number: Issue number to comment on
        comment: Comment text to add

    Returns:
        True if successful, False otherwise.
    """
    try:
        result = _run_gh_command(
            repo_dir,
            "issue",
            "comment",
            str(issue_number),
            "--body",
            comment,
            check=False,
        )
        return result.returncode == 0

    except GitHubOperationError as e:
        logger.error(f"Error commenting on issue #{issue_number} in {repo_dir.name}: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error commenting on issue #{issue_number} in {repo_dir.name}: {str(e)}")
        return False


def create_pull_request(
    repo_dir: Path,
    title: str,
    body: str,
    head: str,
    base: str = "main",
) -> Optional[Dict[str, Any]]:
    """Create a pull request in the repository.

    Args:
        repo_dir: Path to the git repository
        title: PR title
        body: PR body
        head: Branch name to merge from
        base: Branch name to merge into (default: main)

    Returns:
        Dictionary containing PR info (url, number) or None if failed.
    """
    try:
        result = _run_gh_command(
            repo_dir,
            "pr",
            "create",
            "--title",
            title,
            "--body",
            body,
            "--head",
            head,
            "--base",
            base,
            check=False,
        )

        if result.returncode != 0:
            pr_error = result.stderr.strip() or result.stdout.strip()
            logger.error(f"Failed to create PR in {repo_dir.name}: {pr_error}")
            return None

        pr_url = result.stdout.strip()
        pr_number = None
        if pr_url:
            parts = pr_url.rstrip("/").split("/")
            if parts:
                try:
                    pr_number = int(parts[-1])
                except ValueError, IndexError:
                    pass

        return {"url": pr_url, "number": pr_number}

    except GitHubOperationError as e:
        logger.error(f"Error creating PR in {repo_dir.name}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error creating PR in {repo_dir.name}: {str(e)}")
        return None


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
            if "Could not resolve to a Repository" in pr_error:
                logger.warning(
                    f"Cannot access repository {repo_dir.name}: likely permission denied or repository not found. "
                    f"Verify the GitHub token has access to this repository."
                )
            else:
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


def get_pr_for_branch(repo_dir: Path, branch: str) -> Optional[Dict[str, Any]]:
    """Get PR info for a specific branch if it exists.

    Args:
        repo_dir: Path to the git repository
        branch: Branch name to check for PR

    Returns:
        Dictionary with PR info (url, number, state) or None if no PR exists.
    """
    try:
        result = _run_gh_command(
            repo_dir,
            "pr",
            "view",
            branch,
            "--json=number,url,state",
            check=False,
        )

        if result.returncode != 0:
            pr_error = result.stderr.strip() or result.stdout.strip()
            if "no pull request" in pr_error.lower() or "could not find" in pr_error.lower():
                return None
            logger.error(f"Failed to get PR for branch {branch} in {repo_dir.name}: {pr_error}")
            return None

        pr_data = json.loads(result.stdout)
        return {
            "url": pr_data.get("url", ""),
            "number": pr_data.get("number"),
            "state": pr_data.get("state", "UNKNOWN"),
        }

    except GitHubOperationError as e:
        logger.error(f"Error getting PR for branch {branch} from {repo_dir.name}: {str(e)}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse PR JSON for branch {branch} from {repo_dir.name}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error getting PR for branch {branch} from {repo_dir.name}: {str(e)}")
        return None
