"""Vikunja task source for loading Vikunja tasks as tasks.

This module provides a TaskSource implementation that loads tasks from
Vikunja, following the same patterns used by VikunjaWorker.
"""

import logging
from pathlib import Path
from typing import List, Optional

from auto_slopp.utils.git_operations import commit, sanitize_branch_name
from auto_slopp.utils.linking import ensure_issue_link_in_pr_body
from auto_slopp.utils.vikunja_operations import (
    analyze_task,
    comment_on_task,
    find_or_create_project,
    get_open_tasks_by_project,
    update_task_status,
    verify_blocking_closed,
)
from auto_slopp.workers.task_source import Task, TaskSource
from settings.main import settings

logger = logging.getLogger(__name__)


class VikunjaTaskSource(TaskSource):
    """Task source that loads tasks from Vikunja."""

    def _update_task_with_comment_and_status(
        self,
        task_id: int,
        comment: str,
        repo_path: Path,
        status: str | None = None,
        commit_message: str | None = None,
    ) -> bool:
        """Post a comment and optionally update the task status in Vikunja.

        This is a convenience helper that combines :func:`comment_on_task`,
        :func:`update_task_status`, and :func:`commit` into a single call.
        It is used by lifecycle hooks (e.g. ``on_task_complete``,
        ``on_no_changes``, ``on_max_iterations_reached``) to keep the common
        "comment + status transition + commit" pattern DRY.

        Args:
            task_id: Vikunja task ID.
            comment: Comment text to post on the task.
            repo_path: Repository path for committing changes.
            status: Optional new status to set (e.g. "skipped", "failed").
            commit_message: Optional commit message. Defaults to
                ``f"Updated task {task_id}: {status}"`` when ``status`` is
                provided, or ``f"Added comment to task {task_id}"`` otherwise.

        Note:
            If the comment succeeds but the status update fails, a
            comment-only commit is still made (intentional: the posted
            comment is tracked as a commit rather than skipped, so a
            failed status transition does not lose the comment record).

        Returns:
            ``True`` if the comment was posted successfully.  Failures to
            post the comment are logged and return ``False``; status
            transition and commit failures are logged but do not affect
            the return value.
        """
        comment_success = comment_on_task(task_id, comment)
        if not comment_success:
            logger.warning(f"Failed to add comment to task {task_id}")
            return False

        if status:
            status_success = update_task_status(task_id, status)
            if status_success:
                commit_msg = commit_message or f"Updated task {task_id}: {status}"
                commit(repo_path, commit_msg)
                return True
            else:
                logger.warning(f"Failed to update status to '{status}' for task {task_id}")
                # Fall through to add comment commit if status update failed

        commit_msg = commit_message or f"Added comment to task {task_id}"
        commit(repo_path, commit_msg)
        return True

    def get_tasks(self, repo_path: Path) -> List[Task]:
        """Fetch and filter tasks from Vikunja.

        Args:
            repo_path: Path to the repository directory

        Returns:
            List of normalized Task objects ready for processing
        """
        project_name = repo_path.name
        # Create a unique project identifier based on the full path to avoid conflicts
        # between repositories with the same name in different locations
        import hashlib

        path_hash = hashlib.md5(str(repo_path.absolute()).encode(), usedforsecurity=False).hexdigest()[:6]
        project_identifier = f"{project_name[:3]}-{path_hash}".lower()
        # Ensure identifier is exactly 10 characters as per Vikunja requirements
        if len(project_identifier) > 10:
            project_identifier = project_identifier[:10]
        else:
            project_identifier = project_identifier.ljust(10, "-")

        project = find_or_create_project(project_name, project_identifier)
        if not project:
            logger.error(f"Failed to find or create Vikunja project: {project_name}")
            return []

        project_id = project.get("id")
        if not project_id:
            logger.error(f"Project missing ID: {project}")
            return []

        logger.info(f"Using Vikunja project: {project.get('title')} (ID: {project_id})")

        tasks = get_open_tasks_by_project(project_id)

        if not tasks:
            return []

        tasks = self._filter_tasks_by_tag(tasks, settings.github_issue_worker_required_label)

        dep_filtered = []
        for t in tasks:
            if self._has_no_open_dependencies(t["id"]):
                dep_filtered.append(t)
            else:
                logger.info(f"Skipping task #{t['id']} '{t.get('title')}': has open dependencies")
        tasks = dep_filtered

        if not tasks:
            return []

        tasks = sorted(tasks, key=lambda t: t.get("priority", 0), reverse=True)

        normalized_tasks = []
        for task in tasks:
            task_id = task["id"]
            task_title = task["title"]
            task_description = task.get("description", "") or ""

            normalized_task = Task(
                id=task_id,
                title=task_title,
                body=task_description,
                comments=[],
                raw={"_repo_path": repo_path, **task},
            )
            normalized_tasks.append(normalized_task)

        return normalized_tasks

    def get_branch_name(self, task: Task) -> str:
        """Generate the branch name for a Vikunja task.

        Args:
            task: The task to generate a branch name for

        Returns:
            Branch name string (e.g., 'ai/task-42-fix-bug')
        """
        sanitized_title = sanitize_branch_name(task.title[:30].lower())
        return f"ai/task-{task.id}-{sanitized_title}"

    def get_ralph_file_prefix(self) -> str:
        """Return the prefix for ralph task files.

        Returns:
            Prefix string 'vikunja'
        """
        return "vikunja"

    def get_pr_title(self, task: Task) -> str:
        """Generate the PR title for a Vikunja task.

        Args:
            task: The task to generate a PR title for

        Returns:
            PR title string
        """
        return f"Vikunja Task #{task.id}: {task.title}"

    def get_default_pr_body(self, task: Task) -> str:
        """Generate the default PR body for a Vikunja task.

        Args:
            task: The task to generate a PR body for

        Returns:
            PR body string in markdown with a valid closing keyword for the issue
        """
        body = f"Vikunja Task #{task.id}: {task.title}\n\n{task.body}\n\n*This pull request was automatically generated by the VikunjaWorker.*"
        return ensure_issue_link_in_pr_body(body, task.id)

    def on_task_start(self, task: Task, branch_name: str) -> None:
        """Called when task processing begins.

        Updates task status to in_progress, analyzes task for subtasks,
        and adds a start comment.

        Args:
            task: The task being started
            branch_name: The branch created for this task
        """
        repo_path = task.raw.get("_repo_path")
        update_task_status(task.id, "in_progress")
        commit(repo_path, "Updated task status to 'in_progress'")

        subtasks = analyze_task(task.id)
        if subtasks:
            logger.info(f"Created {len(subtasks)} subtasks for task {task.id}")

        start_comment = (
            f"🚀 **Worker Started Processing**\n\n"
            f"Branch: {branch_name}\n\n"
            f"The worker has started processing this task."
        )
        comment_on_task(task.id, start_comment)
        commit(repo_path, f"Added comment to task {task.id}")

    def on_task_complete(self, task: Task, branch_name: str, pr_url: str, findings: Optional[List[str]] = None) -> None:
        """Called when a task completes successfully.

        Updates Vikunja task status to done and adds a comment with the PR URL.
        Uses a single atomic commit for both the status update and comment.

        Args:
            task: The completed task
            branch_name: The branch used for this task
            pr_url: URL of the created pull request
            findings: Optional list of finding strings from PR review (ignored for Vikunja tasks)
        """
        repo_path = task.raw.get("_repo_path")

        pr_info = f"\n\n**Pull Request:** {pr_url}" if pr_url else ""
        success_comment = (
            f"✅ **Task Completed Successfully**\n\n"
            f"**Task:** {task.title}\n\n"
            f"The task has been implemented and pushed to branch `{branch_name}`.\n\n"
            f"**Branch:** {branch_name}{pr_info}\n\n"
            f"Changes have been committed and pushed. The task is ready for review."
        )
        self._update_task_with_comment_and_status(task.id, success_comment, repo_path, "done")

    def on_task_failure(self, task: Task, error: str) -> None:
        """Called when a task fails.

        Updates task status to "failed" and adds a failure comment. The
        status transition is attempted even if posting the comment fails, so
        a task whose comment posting failed still ends up "failed" instead of
        silently staying in its previous status.

        Args:
            task: The failed task
            error: Error description
        """
        repo_path = task.raw.get("_repo_path")
        if repo_path is None:
            logger.error(f"No repo_path found in task #{task.id}, skipping failure handling")
            return

        failure_comment = (
            f"⚠️ **Task Failed: Unexpected Error**\n\n"
            f"An unexpected error occurred while processing the task.\n\n"
            f"**Error:** {error}\n\n"
            f"**Task:** {task.title}\n\n"
            f"This task will not be processed again automatically."
        )
        comment_success = comment_on_task(task.id, failure_comment)
        if comment_success:
            commit(repo_path, f"Added comment to task {task.id}")
        else:
            logger.warning(f"Failed to add failure comment to task {task.id}")

        status_success = update_task_status(task.id, "failed")
        if status_success:
            commit(repo_path, "Updated task status to 'failed'")
        else:
            logger.warning(f"Failed to update status to 'failed' for task {task.id}")

    def on_no_changes(self, task: Task) -> None:
        """Called when no changes were needed for a task.

        Updates Vikunja task status to "done" with a no-changes comment.

        Args:
            task: The task that required no changes
        """
        no_changes_comment = (
            f"✅ **Task Completed: No Changes Required**\n\n"
            f"The task has been reviewed and no modifications were needed.\n\n"
            f"**Task:** {task.title}\n\n"
            f"After analyzing the requirements and exploring the codebase, "
            f"the task was determined to be already complete or not applicable."
        )
        repo_path = task.raw.get("_repo_path")
        if repo_path is None:
            logger.warning(f"No repo_path found in task #{task.id}, skipping no-changes handling")
            return

        self._update_task_with_comment_and_status(
            task_id=task.id,
            comment=no_changes_comment,
            repo_path=repo_path,
            status="done",
            commit_message="Updated task status to 'done'",
        )

    def on_skip(self, task: Task, reason: str) -> None:
        """Called when a task is skipped (e.g., due to LLM unavailability).

        Adds a skip comment to the task but does NOT change the task status:
        Vikunja statuses are per-project and user-defined, so a project may
        not have a status named "skipped" (which would make the status update
        fail on every skip), and ``get_tasks`` only picks up tasks that are
        not ``done``, so leaving the status unchanged keeps the task eligible
        for retry once the LLM is available again.

        Args:
            task: The task being skipped
            reason: Reason for skipping (e.g., "LLM unavailable")
        """
        repo_path = task.raw.get("_repo_path")
        if repo_path is None:
            logger.warning(f"No repo_path found in task #{task.id}, skipping skip handling")
            return

        skip_comment = (
            f"⏭️ **Task Skipped**\n\n"
            f"Reason: {reason}\n\n"
            f"This task will be retried when the LLM becomes available."
        )
        comment_success = comment_on_task(task.id, skip_comment)
        if comment_success:
            commit(repo_path, f"Added comment to task {task.id}")
        else:
            logger.warning(f"Failed to add skip comment to task {task.id}")
        logger.info(f"Added skip comment to task {task.id} (status left unchanged): {reason}")

    def on_max_iterations_reached(self, task: Task, steps_completed: int, total_steps: int, error: str) -> None:
        """Called when the ralph loop reaches max iterations without completing.

        Updates Vikunja task status to "failed" and adds a failure comment.

        Args:
            task: The task that hit the iteration limit
            steps_completed: Number of steps completed
            total_steps: Total number of steps
            error: Last error message
        """
        failure_comment = (
            f"⚠️ **Task Failed: Maximum Iterations Reached**\n\n"
            f" Ralph loop reached maximum iterations without completing all steps.\n\n"
            f"**Progress:**\n"
            f"- Steps completed: {steps_completed}/{total_steps}\n"
            f"- Last error: {error}\n\n"
            f"This task will not be processed again automatically."
        )
        repo_path = task.raw.get("_repo_path")
        if repo_path is None:
            logger.warning(f"No repo_path found in task #{task.id}, skipping max-iterations handling")
            return

        self._update_task_with_comment_and_status(
            task_id=task.id,
            comment=failure_comment,
            repo_path=repo_path,
            status="failed",
            commit_message="Updated task status to 'failed'",
        )

    def _filter_tasks_by_tag(self, tasks: List[dict], tag_name: str) -> List[dict]:
        """Filter tasks to only those whose labels contain a label with a matching title.

        Args:
            tasks: List of task dictionaries from Vikunja
            tag_name: Tag title to filter by (case-insensitive)

        Returns:
            List of tasks that have the specified tag
        """
        tag_lower = tag_name.lower()
        filtered = []
        for task in tasks:
            labels = task.get("labels") or []
            label_titles = [label.get("title", "").lower() for label in labels]
            if tag_lower in label_titles:
                filtered.append(task)
            else:
                logger.info(f"Skipping task #{task.get('id')} '{task.get('title')}': missing tag '{tag_name}'")
        return filtered

    def _has_no_open_dependencies(self, task_id: int) -> bool:
        """Check if a task has no open dependencies.

        Args:
            task_id: The Vikunja task ID

        Returns:
            True if all blocking tasks are closed (or there are none), False otherwise
        """
        try:
            return verify_blocking_closed(task_id)
        except Exception as e:
            logger.warning(f"Failed to verify blocking tasks for task {task_id}: {e}")
            return False
