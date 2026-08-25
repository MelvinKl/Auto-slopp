"""GitHub operations utilities for workers.

This module provides pure functions for common GitHub operations
used across different workers.
"""

import json
import logging
import os
import subprocess
from contextlib import suppress
from pathlib import Path
from typing import Any, Optional

from dotenv import dotenv_values

from settings.main import settings

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
        parsed_env = dotenv_values(settings.additional_env_file)
        # Filter out None values and ensure they are strings to avoid TypeError in subprocess
        for k, v in parsed_env.items():
            if v is not None:
                env[k] = str(v)

    # Ensure GH_TOKEN is set if GITHUB_TOKEN is present (gh cli prefers GH_TOKEN)
    if "GH_TOKEN" not in env and "GITHUB_TOKEN" in env:
        env["GH_TOKEN"] = env["GITHUB_TOKEN"]

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


def get_open_issues(repo_dir: Path) -> list[dict[str, Any]]:
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


def get_issue_comments(repo_dir: Path, issue_number: int) -> list[dict[str, Any]]:
    """Get list of comments on an issue in the repository.

    Args:
        repo_dir: Path to the git repository
        issue_number: Issue number to get comments for

    Returns:
        List of dictionaries containing comment information (id, body, author, createdAt).

    Raises:
        GitHubOperationError: If gh command fails
    """
    try:
        # Use GraphQL API to get comments with databaseId (needed for deletion)
        # gh issue view --json comments doesn't expose databaseId
        owner = settings.github_issue_worker_allowed_creator
        repo = repo_dir.name
        query = (
            '{ repository(owner: "' + owner + '", name: "' + repo + '") '
            "{ issue(number: " + str(issue_number) + ") "
            "{ comments(first: 100) "
            "{ nodes { id databaseId body author { login } createdAt } } } } }"
        )
        result = _run_gh_command(
            repo_dir,
            "api",
            "graphql",
            "-f",
            "query=" + query,
            check=False,
        )

        if result.returncode != 0:
            comment_error = result.stderr.strip() or result.stdout.strip()
            logger.error(f"Failed to get comments for issue #{issue_number} in {repo_dir.name}: {comment_error}")
            return []

        data = json.loads(result.stdout)
        # Extract comments from GraphQL response
        raw_comments = data.get("data", {}).get("repository", {}).get("issue", {}).get("comments", {}).get("nodes", [])
        logger.debug(
            f"[GetComments] Fetched {len(raw_comments)} raw comments for issue #{issue_number} in {repo_dir.name}"
        )

        # Transform to expected format
        comments = []
        for comment in raw_comments:
            comments.append(
                {
                    "id": comment.get("id"),
                    "databaseId": comment.get("databaseId"),
                    "body": comment.get("body", ""),
                    "author": comment.get("author", {}).get("login") if comment.get("author") else None,
                    "createdAt": comment.get("createdAt"),
                }
            )

        logger.debug(f"[GetComments] Transformed {len(comments)} comments for issue #{issue_number}")
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


def delete_issue_comment(repo_dir: Path, issue_number: int, comment_id: int) -> bool:
    """Delete a comment from an issue in the repository.

    Args:
        repo_dir: Path to the git repository
        issue_number: Issue number (not used in the command but kept for consistency)
        comment_id: ID of the comment to delete

    Returns:
        True if successful, False otherwise.
    """
    try:
        logger.debug(f"[DeleteComment] Deleting comment {comment_id} from issue #{issue_number} in {repo_dir.name}")
        # Get repo owner/name from the git remote
        repo_info_result = _run_gh_command(
            repo_dir,
            "repo",
            "view",
            "--json",
            "owner,name",
            check=False,
        )
        if repo_info_result.returncode != 0:
            logger.error(f"Failed to get repo info for {repo_dir.name}")
            return False
        repo_info = json.loads(repo_info_result.stdout)
        owner = repo_info.get("owner", {}).get("login")
        repo_name = repo_info.get("name")
        if not owner or not repo_name:
            logger.error(f"Could not determine owner/repo for {repo_dir.name}")
            return False
        result = _run_gh_command(
            repo_dir,
            "api",
            f"repos/{owner}/{repo_name}/issues/comments/{comment_id}",
            "-X",
            "DELETE",
            check=False,
        )
        if result.returncode == 0:
            logger.debug(f"[DeleteComment] Successfully deleted comment {comment_id}")
        else:
            logger.warning(
                f"[DeleteComment] Failed to delete comment {comment_id}, "
                f"returncode: {result.returncode}, stderr: {result.stderr}"
            )
        return result.returncode == 0

    except GitHubOperationError as e:
        logger.error(f"Error deleting comment #{comment_id} from issue #{issue_number} in {repo_dir.name}: {str(e)}")
        return False
    except Exception as e:
        logger.error(
            f"Unexpected error deleting comment #{comment_id} from issue #{issue_number} in {repo_dir.name}: {str(e)}"
        )
        return False


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
) -> Optional[dict[str, Any]]:
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
                with suppress(ValueError, IndexError):
                    pr_number = int(parts[-1])

        return {"url": pr_url, "number": pr_number}

    except GitHubOperationError as e:
        logger.error(f"Error creating PR in {repo_dir.name}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error creating PR in {repo_dir.name}: {str(e)}")
        return None


def get_open_prs(repo_dir: Path) -> list[dict[str, Any]]:
    """Get list of open PRs in the repository with full information.

    Args:
        repo_dir: Path to the git repository

    Returns:
        List of dictionaries containing PR information (headRefName, author, etc).

    Raises:
        GitHubOperationError: If gh command fails
    """
    try:
        result = _run_gh_command(
            repo_dir,
            "pr",
            "list",
            "--state=open",
            "--json=headRefName,author,number,title",
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
        return prs

    except GitHubOperationError as e:
        logger.error(f"Error getting PRs from {repo_dir.name}: {str(e)}")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse PR list JSON from {repo_dir.name}: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error getting PRs from {repo_dir.name}: {str(e)}")
        return []


def get_closed_prs(repo_dir: Path) -> list[dict[str, Any]]:
    """Get list of closed/merged PRs in the repository with full information.

    Args:
        repo_dir: Path to the git repository

    Returns:
        List of dictionaries containing PR information (headRefName, author, number, title).
        Returns empty list if no closed PRs found or if query fails.

    Raises:
        GitHubOperationError: If gh command fails
    """
    try:
        # gh pr list --state=closed includes both closed and merged PRs
        result = _run_gh_command(
            repo_dir,
            "pr",
            "list",
            "--state=closed",
            "--json=headRefName,author,number,title",
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
                logger.error(f"Failed to list closed PRs in {repo_dir.name}: {pr_error}")
            return []

        prs = json.loads(result.stdout)
        return prs if prs else []

    except GitHubOperationError as e:
        logger.error(f"Error getting closed PRs from {repo_dir.name}: {str(e)}")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse closed PR list JSON from {repo_dir.name}: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error getting closed PRs from {repo_dir.name}: {str(e)}")
        return []


def get_pr_for_branch(repo_dir: Path, branch: str) -> Optional[dict[str, Any]]:
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


def remove_label_from_issue(repo_dir: Path, issue_number: int, label: str) -> bool:
    """Remove a label from an issue in the repository.

    Args:
        repo_dir: Path to the git repository
        issue_number: Issue number to remove label from
        label: Label to remove

    Returns:
        True if successful, False otherwise.
    """
    try:
        result = _run_gh_command(
            repo_dir,
            "issue",
            "edit",
            str(issue_number),
            "--remove-label",
            label,
            check=False,
        )
        return result.returncode == 0

    except GitHubOperationError as e:
        logger.error(f"Error removing label '{label}' from issue #{issue_number} in {repo_dir.name}: {str(e)}")
        return False
    except Exception as e:
        logger.error(
            f"Unexpected error removing label '{label}' from issue #{issue_number} in {repo_dir.name}: {str(e)}"
        )
        return False


def comment_on_pr(repo_dir: Path, pr_number: int, comment: str) -> bool:
    """Add a comment to a pull request in the repository.

    Args:
        repo_dir: Path to the git repository
        pr_number: Pull request number to comment on
        comment: Comment text to add

    Returns:
        True if successful, False otherwise.
    """
    try:
        result = _run_gh_command(
            repo_dir,
            "pr",
            "comment",
            str(pr_number),
            "--body",
            comment,
            check=False,
        )
        return result.returncode == 0

    except GitHubOperationError as e:
        logger.error(f"Error commenting on PR #{pr_number} in {repo_dir.name}: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error commenting on PR #{pr_number} in {repo_dir.name}: {str(e)}")
        return False


def get_pr_diff(repo_dir: Path, pr_number: int) -> Optional[str]:
    """Get the diff of a pull request in the repository.

    Args:
        repo_dir: Path to the git repository
        pr_number: Pull request number to get diff for

    Returns:
        The diff string if successful, None otherwise.
    """
    try:
        result = _run_gh_command(
            repo_dir,
            "pr",
            "diff",
            str(pr_number),
            check=False,
        )
        if result.returncode == 0:
            return result.stdout
        else:
            logger.error(f"Failed to get diff for PR #{pr_number} in {repo_dir.name}: {result.stderr}")
            return None
    except GitHubOperationError as e:
        logger.error(f"Error getting diff for PR #{pr_number} in {repo_dir.name}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error getting diff for PR #{pr_number} in {repo_dir.name}: {str(e)}")
        return None


def get_open_prs_with_label(repo_dir: Path, label: str) -> list[dict]:
    """Get list of open PRs in the repository filtered by label.

    Args:
        repo_dir: Path to the git repository
        label: Label to filter PRs by

    Returns:
        List of dictionaries containing PR information (number, title, body, headRefName, author, labels).

    Raises:
        GitHubOperationError: If gh command fails
    """
    try:
        result = _run_gh_command(
            repo_dir,
            "pr",
            "list",
            "--state=open",
            f"--label={label}",
            "--json=number,title,body,headRefName,author,labels",
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
                logger.error(f"Failed to list PRs with label '{label}' in {repo_dir.name}: {pr_error}")
            return []

        prs = json.loads(result.stdout)
        return prs

    except GitHubOperationError as e:
        logger.error(f"Error getting PRs with label '{label}' from {repo_dir.name}: {str(e)}")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse PR list JSON from {repo_dir.name}: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error getting PRs with label '{label}' from {repo_dir.name}: {str(e)}")
        return []


def get_pr_files(repo_dir: Path, pr_number: int) -> str:
    """Get the full diff text for a pull request.

    Args:
        repo_dir: Path to the git repository
        pr_number: Pull request number to get files for

    Returns:
        The diff text string for the PR.

    Raises:
        GitHubOperationError: If gh command fails
    """
    try:
        result = _run_gh_command(
            repo_dir,
            "pr",
            "diff",
            str(pr_number),
            check=False,
        )

        if result.returncode != 0:
            error_msg = result.stderr.strip() or result.stdout.strip()
            logger.error(f"Failed to get diff for PR #{pr_number} in {repo_dir.name}: {error_msg}")
            raise GitHubOperationError(f"Failed to get PR diff: {error_msg}")

        return result.stdout

    except GitHubOperationError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting diff for PR #{pr_number} in {repo_dir.name}: {str(e)}")
        raise GitHubOperationError(f"Unexpected error getting PR diff: {str(e)}")


def submit_pr_review(repo_dir: Path, pr_number: int, body: str, event: str = "COMMENT") -> bool:
    """Submit a review for a pull request.

    Args:
        repo_dir: Path to the git repository
        pr_number: Pull request number to review
        body: Review body text
        event: Review event type (COMMENT, APPROVE, REQUEST_CHANGES)

    Returns:
        True if successful, False otherwise.
    """
    try:
        # Map event to gh pr review flags
        if event.upper() == "APPROVE":
            event_flag = "--approve"
        elif event.upper() == "REQUEST_CHANGES":
            event_flag = "--request-changes"
        else:  # Default to COMMENT
            event_flag = "--comment"

        result = _run_gh_command(
            repo_dir,
            "pr",
            "review",
            str(pr_number),
            event_flag,
            "--body",
            body,
            check=False,
        )
        return result.returncode == 0

    except GitHubOperationError as e:
        logger.error(f"Error submitting review for PR #{pr_number} in {repo_dir.name}: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error submitting review for PR #{pr_number} in {repo_dir.name}: {str(e)}")
        return False


def get_workflow_runs_for_branch(repo_dir: Path, branch: str, event: Optional[str] = None) -> list[dict[str, Any]]:
    """Get workflow runs for a specific branch, optionally filtered by event.

    Args:
        repo_dir: Path to the git repository
        branch: Branch name to get workflow runs for
        event: Optional event filter (e.g., 'pull_request')

    Returns:
        List of dictionaries containing workflow run information (conclusion, name, etc.)
    """
    try:
        # Get the SHA of the branch to filter by
        sha_result = subprocess.run(
            ["git", "rev-parse", f"origin/{branch}"],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if sha_result.returncode != 0:
            logger.warning(f"Could not resolve origin/{branch} SHA for workflow run lookup")
            return []
        branch_sha = sha_result.stdout.strip()

        result = _run_gh_command(
            repo_dir,
            "run",
            "list",
            "--limit",
            "20",
            "--json",
            "conclusion,name,headSha,event,status,databaseId",
            check=False,
        )

        if result.returncode != 0:
            error_msg = result.stderr.strip() or result.stdout.strip()
            logger.error(f"Failed to list workflow runs for branch {branch} in {repo_dir.name}: {error_msg}")
            return []

        runs = json.loads(result.stdout)
        # Filter by branch SHA since gh run list doesn't support --branch flag
        filtered_runs = [run for run in runs if run.get("headSha") == branch_sha]
        if event:
            filtered_runs = [run for run in filtered_runs if run.get("event") == event]
        return filtered_runs

    except GitHubOperationError as e:
        logger.error(f"Error getting workflow runs for branch {branch} from {repo_dir.name}: {str(e)}")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse workflow runs JSON for branch {branch} from {repo_dir.name}: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error getting workflow runs for branch {branch} from {repo_dir.name}: {str(e)}")
        return []


def _get_failed_job_logs(repo_dir: Path, database_id: Any) -> str:  # noqa: C901
    """Fetch the failed logs of each failed job of a workflow run.

    Args:
        repo_dir: Path to the git repository
        database_id: Database ID of the workflow run

    Returns:
        Concatenated failed job logs, or an empty string if they could not be fetched.
    """
    try:
        jobs_result = _run_gh_command(
            repo_dir,
            "run",
            "view",
            str(database_id),
            "--json",
            "jobs",
            check=False,
            timeout=120,
        )

        if jobs_result.returncode != 0:
            error_msg = jobs_result.stderr.strip() or jobs_result.stdout.strip()
            logger.error(f"Failed to list jobs for workflow run {database_id} in {repo_dir.name}: {error_msg}")
            return ""

        jobs = json.loads(jobs_result.stdout).get("jobs", [])
        chunks = []
        for job in jobs:
            conclusion = job.get("conclusion")
            job_id = job.get("databaseId")
            job_name = job.get("name", "unknown")
            if not job_id or (conclusion and conclusion == "success"):
                continue

            job_result = _run_gh_command(
                repo_dir,
                "run",
                "view",
                str(database_id),
                "--job",
                str(job_id),
                "--log-failed",
                check=False,
                timeout=120,
            )
            if job_result.returncode == 0 and job_result.stdout.strip():
                chunks.append(f"### Failed job: {job_name}\n{job_result.stdout}")

        return "\n\n".join(chunks)

    except GitHubOperationError as e:
        logger.error(f"Error fetching failed job logs for workflow run {database_id} in {repo_dir.name}: {str(e)}")
        return ""
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse jobs JSON for workflow run {database_id} in {repo_dir.name}: {str(e)}")
        return ""
    except Exception as e:
        logger.error(
            f"Unexpected error fetching failed job logs for workflow run {database_id} in {repo_dir.name}: {str(e)}"
        )
        return ""


def get_failed_workflow_logs(repo_dir: Path, run: dict[str, Any]) -> str:
    """Fetch the logs of a single completed, non-successful workflow run.

    Uses ``gh run view <databaseId> --log-failed``. If that is unavailable or
    returns empty output, falls back to fetching the logs of each failed job.

    Args:
        repo_dir: Path to the git repository
        run: Workflow run dictionary (as returned by ``get_workflow_runs_for_branch``)

    Returns:
        The failed log output of the run, or an empty string if it could not be fetched.
    """
    database_id = run.get("databaseId")
    if not database_id:
        logger.warning(f"Workflow run in {repo_dir.name} has no databaseId, cannot fetch logs")
        return ""

    try:
        result = _run_gh_command(
            repo_dir,
            "run",
            "view",
            str(database_id),
            "--log-failed",
            check=False,
            timeout=120,
        )

        if result.returncode == 0 and result.stdout.strip():
            return result.stdout

        if result.returncode != 0:
            error_msg = result.stderr.strip() or result.stdout.strip()
            logger.warning(
                f"gh run view --log-failed returned no usable logs for run {database_id} "
                f"in {repo_dir.name}: {error_msg}"
            )

        logger.info(f"Falling back to failed job logs for run {database_id} in {repo_dir.name}")
        return _get_failed_job_logs(repo_dir, database_id)

    except GitHubOperationError as e:
        logger.error(f"Error fetching logs for workflow run {database_id} in {repo_dir.name}: {str(e)}")
        return ""
    except Exception as e:
        logger.error(f"Unexpected error fetching logs for workflow run {database_id} in {repo_dir.name}: {str(e)}")
        return ""
