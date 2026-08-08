"""Type definitions for the workers package.

Provides TypedDict and dataclass definitions for structured data used
across worker implementations.
"""

from typing import Optional, TypedDict


class TaskResult(TypedDict, total=False):
    """Result of processing a single task.

    Fields that are always present:
        repository: Repository name
        task_id: Task/issue ID
        task_title: Task title
        success: True=success, False=failure, None=skipped
        openagent_executed: Whether an agent was executed
        openagent_executions: Number of agent executions
        task_completed: Whether the task was fully completed
        tasks_completed: Count of fully completed sub-tasks
        pr_created: Whether a PR was created
        prs_created: Count of PRs created
        error: Error message (if any)
        ralph_loops_executed: Number of Ralph loops executed
        ralph_steps_completed: Number of Ralph steps completed

    Optional fields (may be set by specific paths):
        status: Outcome label ('success', 'failure', 'skipped')
        skip_reason: Reason for skipping (when skipped)
        no_changes: True when task required no changes
        pr_url: URL of the created PR
        pr_review_done: True when PR review was performed
        label_removed: True when an automatic label was removed
    """

    repository: str
    task_id: int
    task_title: str
    success: Optional[bool]  # None = skipped
    openagent_executed: bool
    openagent_executions: int
    task_completed: bool
    tasks_completed: int
    pr_created: bool
    prs_created: int
    error: Optional[str]
    ralph_loops_executed: int
    ralph_steps_completed: int
    status: str  # 'success', 'failure', or 'skipped'
    skip_reason: str
    no_changes: bool
    pr_url: str
    pr_review_done: bool
    label_removed: bool
