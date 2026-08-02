"""GitHub task source for loading GitHub issues as tasks.

This module provides a TaskSource implementation that loads tasks from
GitHub Issues, following the same patterns used by GitHubIssueWorker.
"""

import logging
import subprocess
from pathlib import Path
from typing import List, Optional

from auto_slopp.utils.cli_executor import execute_with_instructions
from auto_slopp.utils.git_operations import sanitize_branch_name
from auto_slopp.utils.github_operations import (
    close_issue,
    comment_on_issue,
    delete_issue_comment,
    get_closed_prs,
    get_issue_comments,
    get_open_issues,
    get_open_prs,
    remove_label_from_issue,
)
from auto_slopp.workers.task_source import Task, TaskSource
from settings.main import settings

logger = logging.getLogger(__name__)


class GitHubTaskSource(TaskSource):
    """Task source that loads tasks from GitHub Issues."""

    def get_tasks(self, repo_path: Path) -> List[Task]:
        """Fetch and filter tasks from GitHub Issues.

        Args:
            repo_path: Path to the repository directory

        Returns:
            List of normalized Task objects ready for processing
        """
        issues = get_open_issues(repo_path)

        if not issues:
            return []

        issues = self._filter_renovate_issues(issues)
        issues = self._filter_by_label_and_creator(issues)
        issues = sorted(issues, key=lambda i: i.get("number", 0))

        tasks = []
        for issue in issues:
            issue_number = issue["number"]
            issue_title = issue["title"]
            issue_body = issue.get("body", "") or ""

            issue_author_login = issue.get("author", {}).get("login", "") if issue.get("author") else ""
            comment_texts = self._condense_comments(repo_path, issue_number, issue_author_login)

            task = Task(
                id=issue_number,
                title=issue_title,
                body=issue_body,
                comments=comment_texts,
                raw={"_repo_path": repo_path, **issue},
            )
            tasks.append(task)

        return tasks

    def _condense_comments(self, repo_path: Path, issue_number: int, issue_author_login: str) -> List[str]:
        """Condense all comments (except the issue description) into a single comment.

        Fetches all comments via get_issue_comments(). If there are 0 or 1 comments,
        returns them as-is (no condensing). If there are 2+ comments, calls the CLI
        executor to summarize them, posts the summary as a new comment, deletes the
        original comments, and returns the summary as a single-element list.

        Args:
            repo_path: Path to the repository.
            issue_number: Issue number.
            issue_author_login: Login of the issue author.

        Returns:
            List containing either [] (no comments), [single_comment_body] (one comment),
            or [condensed_summary] (multiple comments condensed).
        """
        # Fetch all comments (each is a dict with 'id', 'body', 'author', 'createdAt')
        all_comments = get_issue_comments(repo_path, issue_number)
        # No comments at all
        if not all_comments:
            return []
        # Single comment: return its body as a single-element list (no condensing)
        if len(all_comments) == 1:
            return [all_comments[0].get("body", "") or ""]
        # Two or more comments: condense ALL comments
        # Prepare prompt for the CLI executor
        comment_lines = []
        for i, comment in enumerate(all_comments, start=1):
            body = comment.get("body", "") or ""
            comment_lines.append(f"Comment {i}:{body}")
        prompt = "\n".join(comment_lines)
        # Execute condensation
        result = execute_with_instructions(
            instructions=prompt,
            work_dir=repo_path,
            agent_args=[],
            task_name="default",
        )
        condensed = ""
        if result and result.get("stdout"):
            condensed = result["stdout"].strip()
        # If condensation produced empty string, fallback to joining with separator
        if not condensed:
            condensed = "\n\n---\n\n".join([c.get("body", "") or "" for c in all_comments])
        # Post the condensed summary as a new comment
        comment_on_issue(repo_path, issue_number, condensed)
        # Delete each original comment
        for comment in all_comments:
            cid = comment.get("id")
            if cid is not None:
                delete_issue_comment(repo_path, issue_number, cid)
        # Return the condensed summary as the sole comment
        return [condensed]

    def get_branch_name(self, task: Task) -> str:
        """Generate the branch name for a GitHub issue task.

        Args:
            task: The task to generate a branch name for

        Returns:
            Branch name string (e.g., 'ai/issue-42-fix-bug')
        """
        sanitized_title = sanitize_branch_name(task.title[:30].lower())
        return f"ai/issue-{task.id}-{sanitized_title}"

    def get_ralph_file_prefix(self) -> str:
        """Return the prefix for ralph task files.

        Returns:
            Prefix string 'github'
        """
        return "github"

    def get_pr_title(self, task: Task) -> str:
        """Generate the PR title for a GitHub issue.

        Args:
            task: The task to generate a PR title for

        Returns:
            PR title string
        """
        return f"#{task.id}: {task.title}"

    def get_default_pr_body(self, task: Task) -> str:
        """Generate the default PR body for a GitHub issue.

        Args:
            task: The task to generate a PR body for

        Returns:
            PR body string in markdown
        """
        return f"Closes #{task.id}\n\n{task.body}"

    def on_task_start(self, task: Task, branch_name: str) -> None:
        """Called when task processing begins.

        For GitHub tasks, this is a no-op since branch creation is handled
        by the worker's execution flow.

        Args:
            task: The task being started
            branch_name: The branch created for this task
        """
        pass

    def on_task_complete(self, task: Task, branch_name: str, pr_url: str, findings: Optional[List[str]] = None) -> None:
        """Called when a task completes successfully.

        If findings is provided and non-empty, adds a comment summarizing the findings
        and does NOT close the issue or remove the automatic work label.
        If findings is None or empty, closes the issue, adds a comment with the PR URL,
        and removes the automatic work label.

        Args:
            task: The completed task
            branch_name: The branch used for this task
            pr_url: URL of the created pull request
            findings: Optional list of finding strings from PR review (e.g., "issue: ...", "suggestion: ...")
        """
        repo_path = task.raw.get("_repo_path")
        if repo_path is None:
            logger.warning(f"No repo_path found in task #{task.id}, skipping completion handling")
            return

        # If findings is provided and non-empty, treat as having review findings
        if findings and len(findings) > 0:
            # Add a comment summarizing the findings
            findings_text = "\n".join(findings)
            comment = f"PR review found {len(findings)} findings that need attention:\n\n{findings_text}"
            comment_success = comment_on_issue(repo_path, task.id, comment)
            if not comment_success:
                logger.warning(f"Failed to add review findings comment to issue #{task.id}")
            # Do NOT close the issue or remove the automatic work label
            return

        # No findings (or findings is None/empty): follow the original behavior
        close_success = close_issue(repo_path, task.id)
        if close_success:
            comment = f"Completed by PR: {pr_url}"
            comment_success = comment_on_issue(repo_path, task.id, comment)
            if not comment_success:
                logger.warning(f"Failed to add comment to issue #{task.id}")
        else:
            logger.warning(f"Failed to close issue #{task.id}")

    def on_task_failure(self, task: Task, error: str) -> None:
        """Called when a task fails.

        For GitHub tasks, this is a no-op. Error handling is managed
        by the worker's execution flow.

        Args:
            task: The failed task
            error: Error description
        """
        pass

    def on_no_changes(self, task: Task) -> None:
        """Called when no changes were needed for a task.

        Closes GitHub issue with a comment indicating no changes were needed,
        but only if there's no evidence that work has been done on the issue.
        If there's evidence of work (comments, PRs, etc.), the issue is kept open
        to allow for future processing.

        Args:
            task: The task that required no changes
        """
        repo_path = task.raw.get("_repo_path")
        if repo_path is None:
            logger.warning(f"No repo_path found in task #{task.id}, skipping no-changes handling")
            return

        # Check if there's evidence that work has been done on this issue
        has_author_comments = self._has_author_comments(repo_path, task.id)
        has_prs = self._has_prs(repo_path, task.id)
        has_recent_activity = self._has_recent_activity(repo_path, task.id)

        if has_author_comments or has_prs or has_recent_activity:
            logger.info(
                f"Issue #{task.id} has evidence of work (author comments: {has_author_comments}, "
                f"PRs: {has_prs}, recent activity: {has_recent_activity}), skipping close"
            )
            return

        no_changes_comment = (
            "No changes required for this issue. The task has been reviewed and no modifications are needed."
        )
        comment_on_issue(repo_path, task.id, no_changes_comment)
        close_issue(repo_path, task.id)

    def on_max_iterations_reached(self, task: Task, steps_completed: int, total_steps: int, error: str) -> None:
        """Called when the ralph loop reaches max iterations without completing.

        Removes the required label from the issue and adds a failure comment.

        Args:
            task: The task that hit the iteration limit
            steps_completed: Number of steps completed
            total_steps: Total number of steps
            error: Last error message
        """
        repo_path = task.raw.get("_repo_path")
        if repo_path is None:
            logger.warning(f"No repo_path found in task #{task.id}, skipping max-iterations handling")
            return

        failure_comment = (
            f"⚠️ **Task Failed: Maximum Iterations Reached**\n\n"
            f" Ralph loop reached maximum iterations without completing all steps.\n\n"
            f"**Progress:**\n"
            f"- Steps completed: {steps_completed}/{total_steps}\n"
            f"- Last error: {error}\n\n"
            f"This issue will not be processed again automatically."
        )
        comment_on_issue(repo_path, task.id, failure_comment)

        label_removed = remove_label_from_issue(
            repo_path,
            task.id,
            settings.github_issue_worker_required_label,
        )
        if label_removed:
            logger.info(f"Removed required label '{settings.github_issue_worker_required_label}' from issue #{task.id}")
        else:
            logger.warning(f"Failed to remove required label from issue #{task.id}")

    def _filter_renovate_issues(self, issues: List[dict]) -> List[dict]:
        """Filter out issues created by Renovate.

        Args:
            issues: List of issue dictionaries

        Returns:
            List of issues with renovate issues removed
        """
        filtered = []
        for issue in issues:
            if self._is_renovate_issue(issue):
                logger.info(f"Skipping renovate issue #{issue.get('number')}: {issue.get('title')}")
            else:
                filtered.append(issue)
        return filtered

    def _is_renovate_issue(self, issue: dict) -> bool:
        """Check if an issue is created by Renovate.

        Args:
            issue: The issue dictionary from GitHub API

        Returns:
            True if the issue is from Renovate, False otherwise
        """
        author = issue.get("author", {})
        author_login = author.get("login", "") if author else ""
        if author_login in ("renovate[bot]", "renovate"):
            return True

        labels = issue.get("labels", [])
        label_names = [label.get("name", "") for label in labels]
        if "renovate" in label_names:
            return True

        return False

    def _should_process_issue(self, issue: dict) -> bool:
        """Check if an issue should be processed based on label and creator.

        Args:
            issue: The issue dictionary from GitHub API

        Returns:
            True if the issue should be processed, False otherwise
        """
        required_label = settings.github_issue_worker_required_label
        allowed_creator = settings.github_issue_worker_allowed_creator

        labels = issue.get("labels", [])
        label_names = [label.get("name", "") for label in labels]
        label_names_lower = [label.lower() for label in label_names]

        has_required_label = required_label.lower() in label_names_lower
        author = issue.get("author", {})
        author_login = author.get("login", "") if author else ""
        is_allowed_creator = author_login == allowed_creator

        return has_required_label and is_allowed_creator

    def _filter_by_label_and_creator(self, issues: List[dict]) -> List[dict]:
        """Filter issues based on required label and allowed creator.

        Args:
            issues: List of issue dictionaries

        Returns:
            List of issues that have the required label or are created by the allowed creator
        """
        filtered = []
        for issue in issues:
            if self._should_process_issue(issue):
                filtered.append(issue)
            else:
                logger.info(
                    f"Skipping issue #{issue.get('number')} '{issue.get('title')}': "
                    f"missing label '{settings.github_issue_worker_required_label}' "
                    f"and not created by '{settings.github_issue_worker_allowed_creator}'"
                )
        return filtered

    def _has_author_comments(self, repo_path: Path, issue_number: int) -> bool:
        """Check if there are comments from the issue author.

        Args:
            repo_path: Path to the repository
            issue_number: Issue number to check

        Returns:
            True if there are comments from the issue author, False otherwise
        """
        try:
            all_comments = get_issue_comments(repo_path, issue_number)
            if not all_comments:
                return False

            issue_author_login = self._get_issue_author_login(repo_path, issue_number)
            if not issue_author_login:
                return False

            author_comments = 0
            for comment in all_comments:
                author = comment.get("author")
                if isinstance(author, dict):
                    author_login = author.get("login")
                else:
                    author_login = author
                if author_login == issue_author_login:
                    author_comments += 1
                    # Check if comment is not the "No changes required" comment we just added
                    if "no changes required for this issue" in comment.get("body", "").lower():
                        author_comments -= 1

            return author_comments > 0

        except Exception as e:
            logger.warning(f"Failed to check author comments for issue #{issue_number}: {str(e)}")
            return False

    def _has_prs(self, repo_path: Path, issue_number: int) -> bool:
        """Check if there are any open or closed PRs for this issue.

        This method checks both open and closed (merged/closed) PRs to determine
        if there's evidence of work done on the issue. A closed PR still indicates
        that changes were made and should prevent the issue from being closed as
        "no changes required".

        Args:
            repo_path: Path to the repository
            issue_number: Issue number to check

        Returns:
            True if there are open or closed PRs for this issue, False otherwise
        """
        try:
            # Check for open PRs
            open_prs = get_open_prs(repo_path)
            if self._pr_mentions_issue(open_prs, issue_number):
                return True

            # Check for closed/merged PRs (evidence of work done)
            closed_prs = get_closed_prs(repo_path)
            if self._pr_mentions_issue(closed_prs, issue_number):
                return True

            return False

        except Exception as e:
            logger.warning(f"Failed to check PRs for issue #{issue_number}: {str(e)}")
            return False

    def _pr_mentions_issue(self, prs: List[dict], issue_number: int) -> bool:
        """Check if any PR in the list mentions the given issue number.

        Args:
            prs: List of PR dictionaries
            issue_number: Issue number to check for

        Returns:
            True if any PR mentions the issue number, False otherwise
        """
        for pr in prs:
            pr_title = pr.get("title", "")
            pr_body = pr.get("body", "")
            pr_head_ref = pr.get("headRefName", "")

            # Check if issue number is mentioned in PR title, body, or head branch
            issue_mentions_in_title = str(issue_number) in pr_title
            issue_mentions_in_body = str(issue_number) in pr_body
            issue_in_branch = str(issue_number) in pr_head_ref

            if issue_mentions_in_title or issue_mentions_in_body or issue_in_branch:
                return True

        return False

    def _has_recent_activity(self, repo_path: Path, issue_number: int) -> bool:
        """Check if there's recent activity on this issue (comments, PR reviews, etc.).

        Args:
            repo_path: Path to the repository
            issue_number: Issue number to check

        Returns:
            True if there's recent activity, False otherwise
        """
        try:
            # Get recent comments
            all_comments = get_issue_comments(repo_path, issue_number)
            if not all_comments:
                return False

            # Check for any comments that are not the standard no-changes comment
            for comment in all_comments:
                body = comment.get("body", "") or ""
                # Skip the standard no-changes comment we would add
                if "no changes required for this issue" in body.lower():
                    continue

                # Any other comment indicates recent activity
                return True

            # Check if there are any workflow runs for recent commits
            try:
                # Get the most recent commits to this repo
                result = subprocess.run(
                    ["git", "log", "--oneline", "-10"],
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode == 0:
                    recent_commits = result.stdout
                    # Check if recent commits mention this issue
                    if str(issue_number) in recent_commits:
                        return True
            except Exception:
                pass

            return False

        except Exception as e:
            logger.warning(f"Failed to check recent activity for issue #{issue_number}: {str(e)}")
            return False

    def _get_issue_author_login(self, repo_path: Path, issue_number: int) -> Optional[str]:
        """Get the author login of an issue.

        Args:
            repo_path: Path to the repository
            issue_number: Issue number to get author for

        Returns:
            Author login string, or None if unable to determine
        """
        try:
            # Get the issue details using gh CLI
            result = subprocess.run(
                ["gh", "issue", "view", str(issue_number), "--json", "author"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                import json

                data = json.loads(result.stdout)
                if data and data.get("author") and isinstance(data["author"], dict):
                    return data["author"].get("login")
            return None
        except Exception as e:
            logger.warning(f"Failed to get issue author for issue #{issue_number}: {str(e)}")
            return None
