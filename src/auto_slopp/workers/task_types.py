"""Type definitions for the workers package.

Provides TypedDict and dataclass definitions for structured data used
across worker implementations.
"""

from enum import Enum, unique
from typing import Literal, NotRequired, Optional, Required, TypedDict


@unique
class TaskStatus(str, Enum):
    """Possible outcomes for a single task.

    Python enums are effectively immutable by design; this decorator
    additionally ensures no duplicate values exist.
    """

    PENDING = "pending"
    SUCCESS = "success"
    SKIPPED = "skipped"
    FAILURE = "failure"


TaskOutcome = bool | None
"""Type alias for task outcome signal.

* ``True``  – Task succeeded.
* ``False`` – Task failed.
* ``None``  – Task was skipped (non-error outcome; always paired with
              ``status == TaskStatus.SKIPPED`` and a descriptive ``skip_reason``).
"""


class TaskResult(TypedDict):
    """Result of processing a single task via IssueWorker.run().

    This TypedDict uses explicit ``Required``/``NotRequired`` markers to
    indicate which fields are always present vs. conditionally set.

    Status values (``status`` field):
        ``"pending"``   – Task was initialised but not yet processed.
        ``"success"``   – Task completed successfully (``success=True``).
        ``"skipped"``   – Task was intentionally skipped (``success=None``).
        ``"failure"``   – Task encountered an error (``success=False``).

    Skip signal semantics (``success`` field) — see :data:`TaskOutcome`:
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
        status: Outcome label (``"pending"``, ``"success"``, ``"skipped"``,
                or ``"failure"``).

    Conditionally set:
        skipped: Legacy convenience flag, ``True`` when
                 ``status == TaskStatus.SKIPPED``.  The canonical skip signal
                 remains ``success=None`` + ``status == TaskStatus.SKIPPED``;
                 ``skipped`` is kept for backward compatibility only.
        skip_reason: Reason for skipping (``Optional[str]``; present when
                     ``status == TaskStatus.SKIPPED``).
        no_changes: True when task required no changes.
        pr_url: URL of the created PR.
        pr_review_done: True when PR review was performed.
        label_removed: True when an automatic label was removed.
    """

    # Required fields (always set by _init_result())
    repository: Required[str]
    task_id: Required[int]
    task_title: Required[str]
    success: Required[TaskOutcome]
    openagent_executed: Required[bool]
    openagent_executions: Required[int]
    task_completed: Required[bool]
    tasks_completed: Required[int]
    pr_created: Required[bool]
    prs_created: Required[int]
    error: Required[Optional[str]]
    ralph_loops_executed: Required[int]
    ralph_steps_completed: Required[int]
    status: Required[Literal["pending", "success", "skipped", "failure"]]

    # Conditionally set fields
    skipped: NotRequired[bool]  # Legacy flag; True when status == TaskStatus.SKIPPED (canonical signal: success=None)
    skip_reason: NotRequired[Optional[str]]  # Present only when status == TaskStatus.SKIPPED
    no_changes: NotRequired[bool]
    pr_url: NotRequired[str]
    pr_review_done: NotRequired[bool]
    label_removed: NotRequired[bool]


def validate_task_result(result: TaskResult) -> None:
    """Validate that skipped field is consistent with status and success field.

    Args:
        result: The TaskResult to validate.

    Raises:
        ValueError: If status is not one of the TaskStatus values,
            if the result is not in a terminal state (status=PENDING),
            if skipped field is inconsistent with status, or if
            success=None is inconsistent with status=SKIPPED.
    """
    skipped = result.get("skipped")
    status = result.get("status")
    success = result.get("success")

    # A missing or typo'd status must not fall through to the success-based
    # branch in run(); it must be caught by the same invariant.
    if status not in {s.value for s in TaskStatus}:
        raise ValueError(f"Invalid task status: {status!r}; must be one of " f"{sorted(s.value for s in TaskStatus)}")

    # All results reaching run() must have a terminal status; a leaked
    # PENDING result would otherwise be silently counted as a success.
    if status == TaskStatus.PENDING:
        raise ValueError("Task result must have a terminal status, got 'pending'")

    if status == TaskStatus.SKIPPED and skipped is not True:
        raise ValueError("When status is SKIPPED, skipped must be True")
    if status != TaskStatus.SKIPPED and skipped is True:
        raise ValueError("skipped can only be True when status is SKIPPED")

    # Validate canonical skip signal: success=None <-> status=SKIPPED
    if success is None and status != TaskStatus.SKIPPED:
        raise ValueError("When success is None, status must be SKIPPED")
    if status == TaskStatus.SKIPPED and success is not None:
        raise ValueError("When status is SKIPPED, success must be None")
