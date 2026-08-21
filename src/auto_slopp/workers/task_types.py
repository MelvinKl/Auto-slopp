"""Type definitions for the workers package.

Provides TypedDict and dataclass definitions for structured data used
across worker implementations.
"""

from typing import Optional, TypedDict


class TaskResult(TypedDict, total=False):
    """Result of processing a single task via IssueWorker.run().

    This TypedDict uses ``total=False``, meaning all fields are optional at the
    type level.  In practice the ``_init_result()`` helper always populates the
    core fields listed under "Always set" before the result is returned or
    passed to callbacks.

    Status values (``status`` field):
        ``"pending"``   – Task was initialised but not yet processed.
        ``"success"``   – Task completed successfully (``success=True``).
        ``"skipped"``   – Task was intentionally skipped (``success=None``).
        ``"failure"``   – Task encountered an error (``success=False``).

    Skip signal semantics (``success`` field):
        ``True``  – Task succeeded.
        ``False`` – Task failed.
        ``None``  – Task was skipped (non-error outcome; always paired with
                    ``status == "skipped"`` and a descriptive ``skip_reason``).

    Always set (by ``_init_result()``):
        repository: Repository name.
        task_id: Task/issue ID.
        task_title: Task title.
        success: Initialised to ``True``; set to ``None`` on skip or ``False``
                 on failure.
        openagent_executed: Whether an agent was executed.
        openagent_executions: Number of agent executions.
        task_completed: Whether the task was fully completed.
        tasks_completed: Count of fully completed sub-tasks.
        pr_created: Whether a PR was created.
        prs_created: Count of PRs created.
        error: Error message (if any).
        ralph_loops_executed: Number of Ralph loops executed.
        ralph_steps_completed: Number of Ralph steps completed.
        status: Outcome label (``"pending"``, ``"success"``, ``"skipped"``, or
                ``"failure"``).

    Conditionally set:
        skipped: Legacy convenience flag, ``True`` when
                 ``status == "skipped"``.  The canonical skip signal remains
                 ``success=None`` + ``status == "skipped"``; ``skipped`` is
                 kept for backward compatibility only.
        skip_reason: Reason for skipping (``Optional[str]``; present when
                     ``status == "skipped"``).
        no_changes: True when task required no changes.
        pr_url: URL of the created PR.
        pr_review_done: True when PR review was performed.
        label_removed: True when an automatic label was removed.
    """

    repository: str
    task_id: int
    task_title: str
    success: Optional[bool]  # None = skipped, True = success, False = failure
    openagent_executed: bool
    openagent_executions: int
    task_completed: bool
    tasks_completed: int
    pr_created: bool
    prs_created: int
    error: Optional[str]
    ralph_loops_executed: int
    ralph_steps_completed: int
    status: str  # 'pending', 'success', 'failure', or 'skipped'
    skipped: bool  # Legacy flag; True when status == "skipped" (canonical signal: success=None)
    skip_reason: Optional[str]  # Present only when status == "skipped"
    no_changes: bool
    pr_url: str
    pr_review_done: bool
    label_removed: bool
