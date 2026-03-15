"""Task executor with loop-based execution and progress tracking.

This module provides an improved execution pattern that:
1. Executes tasks in discrete steps
2. Tracks progress across steps
3. Implements verification loops
4. Supports retry with refined instructions
"""

import json
import logging
import re
import subprocess
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class StepStatus(str, Enum):
    """Status of a task execution step."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ExecutionStep(str, Enum):
    """Steps in the task execution process."""

    FETCH = "fetch"
    VALIDATE = "validate"
    PREPARE = "prepare"
    EXECUTE = "execute"
    VERIFY = "verify"
    FINALIZE = "finalize"


class TaskProgress:
    """Tracks progress of task execution across steps."""

    def __init__(self, task_id: str, work_dir: Path):
        self.task_id = task_id
        self.work_dir = work_dir
        self.steps: Dict[ExecutionStep, StepStatus] = {step: StepStatus.PENDING for step in ExecutionStep}
        self.iteration = 0
        self.max_iterations = 3
        self.errors: List[str] = []
        self.metadata: Dict[str, Any] = {}

    def mark_step(self, step: ExecutionStep, status: StepStatus) -> None:
        """Mark a step with a specific status."""
        self.steps[step] = status
        logger.info(f"Task {self.task_id}: Step {step.value} marked as {status.value}")

    def get_step_status(self, step: ExecutionStep) -> StepStatus:
        """Get the status of a specific step."""
        return self.steps.get(step, StepStatus.PENDING)

    def is_step_completed(self, step: ExecutionStep) -> bool:
        """Check if a step is completed."""
        return self.get_step_status(step) == StepStatus.COMPLETED

    def add_error(self, error: str) -> None:
        """Add an error to the error log."""
        self.errors.append(error)
        logger.error(f"Task {self.task_id}: {error}")

    def increment_iteration(self) -> bool:
        """Increment iteration counter and check if more iterations allowed."""
        self.iteration += 1
        return self.iteration < self.max_iterations

    def can_retry(self) -> bool:
        """Check if retry is possible."""
        return self.iteration < self.max_iterations

    def to_dict(self) -> Dict[str, Any]:
        """Convert progress to dictionary for serialization."""
        return {
            "task_id": self.task_id,
            "work_dir": str(self.work_dir),
            "steps": {step.value: status.value for step, status in self.steps.items()},
            "iteration": self.iteration,
            "max_iterations": self.max_iterations,
            "errors": self.errors,
            "metadata": self.metadata,
        }

    def save(self, file_path: Optional[Path] = None) -> None:
        """Save progress to a JSON file."""
        if file_path is None:
            file_path = self.work_dir / f".task_progress_{self.task_id}.json"

        try:
            with open(file_path, "w") as f:
                json.dump(self.to_dict(), f, indent=2)
            logger.debug(f"Saved task progress to {file_path}")
        except Exception as e:
            logger.warning(f"Failed to save task progress: {e}")

    @classmethod
    def load(cls, file_path: Path) -> Optional["TaskProgress"]:
        """Load progress from a JSON file."""
        try:
            with open(file_path, "r") as f:
                data = json.load(f)

            progress = cls(task_id=data["task_id"], work_dir=Path(data["work_dir"]))
            progress.steps = {ExecutionStep(step): StepStatus(status) for step, status in data["steps"].items()}
            progress.iteration = data["iteration"]
            progress.max_iterations = data["max_iterations"]
            progress.errors = data["errors"]
            progress.metadata = data.get("metadata", {})

            return progress
        except Exception as e:
            logger.warning(f"Failed to load task progress: {e}")
            return None


class IssueTracker:
    """Tracks execution progress and can be stored in GitHub issue comments."""

    TRACKER_MARKER = "<!-- ISSUE_TRACKER -->"

    def __init__(
        self,
        issue_number: int,
        issue_title: str,
        branch_name: str,
        max_iterations: int = 3,
    ):
        self.issue_number = issue_number
        self.issue_title = issue_title
        self.branch_name = branch_name
        self.max_iterations = max_iterations
        self.steps: Dict[ExecutionStep, StepStatus] = {step: StepStatus.PENDING for step in ExecutionStep}
        self.step_timestamps: Dict[ExecutionStep, str] = {}
        self.iteration = 0
        self.errors: List[str] = []
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()

    def mark_step(self, step: ExecutionStep, status: StepStatus) -> None:
        """Mark a step with a specific status and update timestamp."""
        self.steps[step] = status
        self.step_timestamps[step] = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        logger.info(f"Issue #{self.issue_number}: Step {step.value} marked as {status.value}")

    def get_step_status(self, step: ExecutionStep) -> StepStatus:
        """Get the status of a specific step."""
        return self.steps.get(step, StepStatus.PENDING)

    def is_step_completed(self, step: ExecutionStep) -> bool:
        """Check if a step is completed."""
        return self.get_step_status(step) == StepStatus.COMPLETED

    def add_error(self, error: str) -> None:
        """Add an error to the error log."""
        self.errors.append(error)
        self.updated_at = datetime.now().isoformat()
        logger.error(f"Issue #{self.issue_number}: {error}")

    def increment_iteration(self) -> bool:
        """Increment iteration counter and check if more iterations allowed."""
        self.iteration += 1
        self.updated_at = datetime.now().isoformat()
        return self.iteration < self.max_iterations

    def can_retry(self) -> bool:
        """Check if retry is possible."""
        return self.iteration < self.max_iterations

    def to_markdown(self) -> str:
        """Convert tracker to markdown format for GitHub comment."""
        lines = [
            f"{self.TRACKER_MARKER}",
            f"# Implementation Tracker: Issue #{self.issue_number}",
            "",
            f"**Issue**: {self.branch_name}",
            f"**Title**: {self.issue_title}",
            f"**Created**: {self.created_at}",
            f"**Updated**: {self.updated_at}",
            f"**Iteration**: {self.iteration}/{self.max_iterations}",
            "",
            "## Execution Steps",
            "",
        ]

        for step in ExecutionStep:
            status = self.steps.get(step, StepStatus.PENDING)
            timestamp = self.step_timestamps.get(step, "")
            status_emoji = {
                StepStatus.PENDING: "⏳",
                StepStatus.IN_PROGRESS: "🔄",
                StepStatus.COMPLETED: "✅",
                StepStatus.FAILED: "❌",
                StepStatus.SKIPPED: "⏭️",
            }.get(status, "❓")

            timestamp_str = f" ({timestamp})" if timestamp else ""
            lines.append(f"- {status_emoji} **{step.value.upper()}**: {status.value}{timestamp_str}")

        if self.errors:
            lines.extend(
                [
                    "",
                    "## Errors",
                    "",
                ]
            )
            for i, error in enumerate(self.errors, 1):
                lines.append(f"{i}. {error}")

        lines.extend(
            [
                "",
                f"{self.TRACKER_MARKER}",
            ]
        )

        return "\n".join(lines)

    @classmethod
    def from_markdown(cls, markdown: str) -> Optional["IssueTracker"]:
        """Parse tracker from markdown format."""
        if cls.TRACKER_MARKER not in markdown:
            return None

        try:
            lines = markdown.split("\n")
            data = {}

            for line in lines:
                if line.startswith("**Issue**:"):
                    data["branch_name"] = line.split(":", 1)[1].strip()
                elif line.startswith("**Title**:"):
                    data["issue_title"] = line.split(":", 1)[1].strip()
                elif line.startswith("**Created**:"):
                    data["created_at"] = line.split(":", 1)[1].strip()
                elif line.startswith("**Updated**:"):
                    data["updated_at"] = line.split(":", 1)[1].strip()
                elif line.startswith("**Iteration**:"):
                    iteration_str = line.split(":", 1)[1].strip()
                    parts = iteration_str.split("/")
                    data["iteration"] = int(parts[0]) if parts else 0
                    data["max_iterations"] = int(parts[1]) if len(parts) > 1 else 3

            if "branch_name" not in data or "issue_title" not in data:
                return None

            issue_number_match = re.search(r"issue-(\d+)", data["branch_name"])
            if not issue_number_match:
                return None

            issue_number = int(issue_number_match.group(1))

            tracker = cls(
                issue_number=issue_number,
                issue_title=data["issue_title"],
                branch_name=data["branch_name"],
                max_iterations=data.get("max_iterations", 3),
            )

            tracker.created_at = data.get("created_at", tracker.created_at)
            tracker.updated_at = data.get("updated_at", tracker.updated_at)
            tracker.iteration = data.get("iteration", 0)

            step_pattern = r"- [^\s]+ \*\*([A-Z]+)\*\*: (\w+)"
            for line in lines:
                match = re.search(step_pattern, line)
                if match:
                    step_name = match.group(1).lower()
                    status_name = match.group(2).lower()
                    try:
                        step = ExecutionStep(step_name)
                        status = StepStatus(status_name)
                        tracker.steps[step] = status
                    except ValueError:
                        pass

            error_pattern = r"^\d+\. (.+)$"
            in_errors_section = False
            for line in lines:
                if "## Errors" in line:
                    in_errors_section = True
                    continue
                if in_errors_section and line.startswith("##"):
                    break
                if in_errors_section:
                    match = re.match(error_pattern, line)
                    if match:
                        tracker.errors.append(match.group(1))

            return tracker

        except Exception as e:
            logger.warning(f"Failed to parse issue tracker from markdown: {e}")
            return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert tracker to dictionary for serialization."""
        return {
            "issue_number": self.issue_number,
            "issue_title": self.issue_title,
            "branch_name": self.branch_name,
            "steps": {step.value: status.value for step, status in self.steps.items()},
            "step_timestamps": self.step_timestamps,
            "iteration": self.iteration,
            "max_iterations": self.max_iterations,
            "errors": self.errors,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


def run_verification_tests(work_dir: Path, timeout: int = 300) -> Dict[str, Any]:
    """Run tests to verify task execution was successful.

    Args:
        work_dir: Directory to run tests in
        timeout: Timeout for test execution

    Returns:
        Dictionary with test results
    """
    logger.info(f"Running verification tests in {work_dir}")

    result = {
        "success": False,
        "tests_passed": False,
        "lint_passed": False,
        "error_output": "",
    }

    try:
        test_result = subprocess.run(
            ["make", "test"],
            cwd=work_dir,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        result["tests_passed"] = test_result.returncode == 0
        result["test_output"] = test_result.stdout + test_result.stderr

        if test_result.returncode != 0:
            result["error_output"] = test_result.stdout + test_result.stderr
            logger.warning(f"Tests failed in {work_dir}")
        else:
            logger.info(f"Tests passed in {work_dir}")

    except subprocess.TimeoutExpired:
        result["error_output"] = f"Test execution timed out after {timeout}s"
        logger.error(result["error_output"])
    except FileNotFoundError:
        logger.info("No Makefile found, skipping make test")
        result["tests_passed"] = True
    except Exception as e:
        result["error_output"] = f"Error running tests: {str(e)}"
        logger.error(result["error_output"])

    result["success"] = result["tests_passed"]
    return result


def build_retry_instructions(
    original_instructions: str,
    error_output: str,
    iteration: int,
) -> str:
    """Build refined instructions for retry attempts.

    Args:
        original_instructions: Original task instructions
        error_output: Error output from failed execution
        iteration: Current iteration number

    Returns:
        Refined instructions string
    """
    retry_context = (
        f"\n\n"
        f"=== RETRY ATTEMPT {iteration} ===\n"
        f"The previous execution attempt failed. Here is the error output:\n"
        f"```\n{error_output}\n```\n\n"
        f"Please analyze the error and fix the issue. Focus on:\n"
        f"1. Understanding what went wrong\n"
        f"2. Making the necessary corrections\n"
        f"3. Ensuring tests pass with 'make test'\n"
    )

    return original_instructions + retry_context


def load_tracker_from_comments(
    comments: List[Dict[str, Any]],
    issue_number: int,
    issue_title: str,
    branch_name: str,
    max_iterations: int = 3,
) -> IssueTracker:
    """Load issue tracker from GitHub comments or create a new one.

    Args:
        comments: List of comments from GitHub issue
        issue_number: Issue number
        issue_title: Issue title
        branch_name: Branch name for this issue
        max_iterations: Maximum iterations for new tracker

    Returns:
        IssueTracker instance (loaded from comment or newly created)
    """
    for comment in reversed(comments):
        body = comment.get("body", "")
        if IssueTracker.TRACKER_MARKER in body:
            tracker = IssueTracker.from_markdown(body)
            if tracker:
                logger.info(f"Loaded existing tracker for issue #{issue_number}")
                return tracker

    logger.info(f"Creating new tracker for issue #{issue_number}")
    return IssueTracker(
        issue_number=issue_number,
        issue_title=issue_title,
        branch_name=branch_name,
        max_iterations=max_iterations,
    )


def update_tracker_comment(
    tracker: IssueTracker,
    comments: List[Dict[str, Any]],
    comment_func: Any,
    issue_number: int,
) -> bool:
    """Update or create tracker comment on GitHub issue.

    Args:
        tracker: IssueTracker instance to update
        comments: List of existing comments
        comment_func: Function to add comment (e.g., comment_on_issue)
        issue_number: Issue number to comment on

    Returns:
        True if successful, False otherwise
    """
    tracker_markdown = tracker.to_markdown()
    return comment_func(issue_number, tracker_markdown)


def execute_task_with_loop(
    instructions: str,
    work_dir: Path,
    execute_func: Any,
    max_iterations: int = 3,
    verify_tests: bool = True,
    task_id: Optional[str] = None,
    **execute_kwargs: Any,
) -> Dict[str, Any]:
    """Execute a task with loop-based verification and retry.

    This implements a loop pattern where:
    1. Execute the task
    2. Verify results (run tests)
    3. If failed, retry with refined instructions
    4. Repeat until success or max iterations

    Args:
        instructions: Task instructions
        work_dir: Working directory
        execute_func: Function to execute the task (e.g., execute_with_instructions)
        max_iterations: Maximum number of retry iterations
        verify_tests: Whether to run tests for verification
        task_id: Optional task identifier for progress tracking
        **execute_kwargs: Additional arguments for execute_func

    Returns:
        Dictionary with execution results
    """
    task_id = task_id or work_dir.name
    progress = TaskProgress(task_id=task_id, work_dir=work_dir)
    progress.max_iterations = max_iterations

    result = {
        "success": False,
        "iterations": 0,
        "tests_passed": False,
        "final_instructions": instructions,
        "progress": progress.to_dict(),
    }

    progress.mark_step(ExecutionStep.FETCH, StepStatus.COMPLETED)
    progress.mark_step(ExecutionStep.VALIDATE, StepStatus.COMPLETED)
    progress.mark_step(ExecutionStep.PREPARE, StepStatus.IN_PROGRESS)

    current_instructions = instructions

    while progress.can_retry():
        iteration = progress.iteration + 1
        logger.info(f"Task {task_id}: Starting iteration {iteration}/{max_iterations}")

        progress.mark_step(ExecutionStep.PREPARE, StepStatus.COMPLETED)
        progress.mark_step(ExecutionStep.EXECUTE, StepStatus.IN_PROGRESS)

        exec_result = execute_func(
            instructions=current_instructions,
            work_dir=work_dir,
            **execute_kwargs,
        )

        if not exec_result.get("success", False):
            error_msg = exec_result.get("error", "Unknown execution error")
            progress.add_error(f"Iteration {iteration} execution failed: {error_msg}")
            progress.mark_step(ExecutionStep.EXECUTE, StepStatus.FAILED)

            if progress.increment_iteration():
                current_instructions = build_retry_instructions(
                    original_instructions=instructions,
                    error_output=error_msg,
                    iteration=iteration,
                )
                continue
            else:
                break

        progress.mark_step(ExecutionStep.EXECUTE, StepStatus.COMPLETED)

        if not verify_tests:
            result["success"] = True
            result["iterations"] = iteration
            progress.mark_step(ExecutionStep.VERIFY, StepStatus.SKIPPED)
            progress.mark_step(ExecutionStep.FINALIZE, StepStatus.COMPLETED)
            break

        progress.mark_step(ExecutionStep.VERIFY, StepStatus.IN_PROGRESS)
        verify_result = run_verification_tests(work_dir)

        if verify_result["success"]:
            logger.info(f"Task {task_id}: Verification passed on iteration {iteration}")
            result["success"] = True
            result["iterations"] = iteration
            result["tests_passed"] = True
            progress.mark_step(ExecutionStep.VERIFY, StepStatus.COMPLETED)
            progress.mark_step(ExecutionStep.FINALIZE, StepStatus.COMPLETED)
            break
        else:
            error_output = verify_result.get("error_output", "Unknown test error")
            progress.add_error(f"Iteration {iteration} verification failed: {error_output}")
            progress.mark_step(ExecutionStep.VERIFY, StepStatus.FAILED)

            if progress.increment_iteration():
                current_instructions = build_retry_instructions(
                    original_instructions=instructions,
                    error_output=error_output,
                    iteration=iteration,
                )
                progress.steps[ExecutionStep.EXECUTE] = StepStatus.PENDING
                progress.steps[ExecutionStep.VERIFY] = StepStatus.PENDING
            else:
                break

    result["progress"] = progress.to_dict()
    result["final_instructions"] = current_instructions

    if not result["success"]:
        logger.error(
            f"Task {task_id}: Failed after {progress.iteration} iterations. " f"Errors: {'; '.join(progress.errors)}"
        )

    return result
