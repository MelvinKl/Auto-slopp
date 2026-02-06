"""
Merge conflict detection and escalation system for Auto-slopp.

This module provides comprehensive merge conflict detection, classification,
logging, and escalation functionality with OpenCode integration.
"""

import json
import os
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

from ..config import get_config
from ..logging import get_logger

logger = get_logger(__name__)


class MergeErrorType(Enum):
    """Classification of merge error types."""

    NETWORK_FAILURE = "NETWORK_FAILURE"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    REPOSITORY_CORRUPTION = "REPOSITORY_CORRUPTION"
    MERGE_CONFLICT = "MERGE_CONFLICT"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"


class MergeResolutionStatus(Enum):
    """Status of merge resolution attempts."""

    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    MANUAL_INTERVENTION_REQUIRED = "MANUAL_INTERVENTION_REQUIRED"
    RETRY_RECOMMENDED = "RETRY_RECOMMENDED"


@dataclass
class MergeAttempt:
    """Data structure for merge attempt logging."""

    operation_id: str
    source_branch: str
    target_branch: str
    source_commit: str
    target_commit: str
    timestamp: datetime
    status: str = "ATTEMPTED"
    error_type: Optional[MergeErrorType] = None
    error_message: Optional[str] = None


@dataclass
class ConflictReport:
    """Data structure for merge conflict reports."""

    operation_id: str
    conflicted_files: List[str]
    conflict_details: Dict[str, Any]
    timestamp: datetime
    repository_state: Dict[str, Any]


@dataclass
class OpenCodeEscalation:
    """Data structure for OpenCode escalation logging."""

    operation_id: str
    escalation_type: str
    context_file: Optional[str]
    context_data: Dict[str, Any]
    timestamp: datetime
    resolution_status: Optional[str] = None


class MergeConflictDetector:
    """Detects and classifies merge conflicts."""

    def __init__(self, config=None):
        self.config = config or get_config()
        self.logger = get_logger(f"{__name__}.detector")

    def classify_merge_error(self, exit_code: int, error_output: str) -> MergeErrorType:
        """
        Classify merge error based on exit code and error output.

        Args:
            exit_code: Git command exit code
            error_output: Error message from git command

        Returns:
            MergeErrorType: Classified error type
        """
        error_output_lower = error_output.lower()

        # Network-related errors
        if (
            exit_code == 128
            or "connection refused" in error_output_lower
            or "failed to connect" in error_output_lower
            or "network" in error_output_lower
            or "timeout" in error_output_lower
        ):
            return MergeErrorType.NETWORK_FAILURE

        # Permission errors
        if (
            "permission denied" in error_output_lower
            or "access denied" in error_output_lower
            or "authentication failed" in error_output_lower
        ):
            return MergeErrorType.PERMISSION_DENIED

        # Repository corruption
        if (
            "corrupt" in error_output_lower
            or "invalid" in error_output_lower
            or "bad object" in error_output_lower
            or "not a git repository" in error_output_lower
        ):
            return MergeErrorType.REPOSITORY_CORRUPTION

        # Merge conflicts
        if exit_code == 1 and (
            "merge conflict" in error_output_lower
            or "<<<<<<<" in error_output_lower
            or "======= " in error_output_lower
            or ">>>>>>>" in error_output_lower
        ):
            return MergeErrorType.MERGE_CONFLICT

        return MergeErrorType.UNKNOWN_ERROR

    def detect_conflicted_files(self) -> List[str]:
        """
        Detect files with merge conflicts.

        Returns:
            List[str]: List of conflicted file paths
        """
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "--diff-filter=U"],
                capture_output=True,
                text=True,
                check=True,
            )
            conflicted_files = (
                result.stdout.strip().split("\n") if result.stdout.strip() else []
            )
            return [f for f in conflicted_files if f]

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to detect conflicted files: {e}")
            return []

    def get_conflict_details(self, file_path: str) -> Dict[str, Any]:
        """
        Get detailed conflict information for a specific file.

        Args:
            file_path: Path to the conflicted file

        Returns:
            Dict[str, Any]: Detailed conflict information
        """
        try:
            # Get conflict markers count
            result = subprocess.run(
                ["git", "diff", "--unified=0", file_path],
                capture_output=True,
                text=True,
                check=True,
            )

            conflict_content = result.stdout
            marker_count = conflict_content.count("<<<<<<<")

            # Get file status
            status_result = subprocess.run(
                ["git", "status", "--porcelain", file_path],
                capture_output=True,
                text=True,
                check=True,
            )

            return {
                "file_path": file_path,
                "conflict_markers": marker_count,
                "status": status_result.stdout.strip(),
                "has_conflicts": marker_count > 0,
            }

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to get conflict details for {file_path}: {e}")
            return {
                "file_path": file_path,
                "conflict_markers": 0,
                "status": "unknown",
                "has_conflicts": False,
                "error": str(e),
            }


class MergeEscalationEngine:
    """Handles escalation of merge conflicts to OpenCode."""

    def __init__(self, config=None):
        self.config = config or get_config()
        self.logger = get_logger(f"{__name__}.escalation")
        self.detector = MergeConflictDetector(config)

    def create_conflict_report(self, operation_id: str) -> ConflictReport:
        """
        Create a comprehensive conflict report.

        Args:
            operation_id: Unique identifier for the operation

        Returns:
            ConflictReport: Detailed conflict report
        """
        conflicted_files = self.detector.detect_conflicted_files()
        conflict_details = {}

        for file_path in conflicted_files:
            conflict_details[file_path] = self.detector.get_conflict_details(file_path)

        # Get repository state
        repo_state = self._get_repository_state()

        return ConflictReport(
            operation_id=operation_id,
            conflicted_files=conflicted_files,
            conflict_details=conflict_details,
            timestamp=datetime.now(),
            repository_state=repo_state,
        )

    def preserve_state_for_opencode(
        self, operation_id: str, error_type: MergeErrorType
    ) -> str:
        """
        Preserve repository state for OpenCode analysis.

        Args:
            operation_id: Unique identifier for the operation
            error_type: Type of error that occurred

        Returns:
            str: Path to the preserved state directory
        """
        state_dir = Path(tempfile.mkdtemp(prefix=f"opencode_state_{operation_id}_"))

        try:
            # Save git status
            status_file = state_dir / "git_status.txt"
            subprocess.run(
                ["git", "status", "--porcelain", "-v"],
                stdout=status_file.open("w"),
                check=True,
            )

            # Save conflicted files
            conflicted_files = self.detector.detect_conflicted_files()
            for file_path in conflicted_files:
                dest_file = state_dir / "conflicts" / Path(file_path).name
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                subprocess.run(["cp", file_path, dest_file], check=True)

            # Save conflict report
            conflict_report = self.create_conflict_report(operation_id)
            report_file = state_dir / "conflict_report.json"
            report_file.write_text(
                json.dumps(asdict(conflict_report), indent=2, default=str)
            )

            # Save error context
            error_context = {
                "operation_id": operation_id,
                "error_type": error_type.value,
                "timestamp": datetime.now().isoformat(),
                "working_directory": os.getcwd(),
                "git_branch": self._get_current_branch(),
            }

            context_file = state_dir / "error_context.json"
            context_file.write_text(json.dumps(error_context, indent=2))

            self.logger.info(f"State preserved for OpenCode: {state_dir}")
            return str(state_dir)

        except Exception as e:
            self.logger.error(f"Failed to preserve state for OpenCode: {e}")
            # Clean up on failure
            import shutil

            shutil.rmtree(state_dir, ignore_errors=True)
            raise

    def escalate_to_opencode(
        self, operation_id: str, conflict_report: ConflictReport
    ) -> Dict[str, Any]:
        """
        Escalate conflict to OpenCode for resolution.

        Args:
            operation_id: Unique identifier for the operation
            conflict_report: Detailed conflict report

        Returns:
            Dict[str, Any]: Escalation response
        """
        # Preserve state first
        state_dir = self.preserve_state_for_opencode(
            operation_id, MergeErrorType.MERGE_CONFLICT
        )

        # Create escalation prompt
        escalation_prompt = self._create_opencode_prompt(conflict_report, state_dir)

        # Log escalation
        escalation = OpenCodeEscalation(
            operation_id=operation_id,
            escalation_type="merge_conflict_resolution",
            context_file=state_dir,
            context_data=asdict(conflict_report),
            timestamp=datetime.now(),
        )

        self._log_escalation(escalation)

        # In a real implementation, this would call OpenCode API
        # For now, we'll simulate the response
        response = {
            "escalation_id": f"opencode_{operation_id}",
            "status": "queued",
            "estimated_resolution_time": "5-10 minutes",
            "state_directory": state_dir,
            "prompt": escalation_prompt,
        }

        self.logger.info(f"Escalated to OpenCode: {response['escalation_id']}")
        return response

    def _create_opencode_prompt(
        self, conflict_report: ConflictReport, state_dir: str
    ) -> str:
        """Create detailed prompt for OpenCode resolution."""

        prompt = f"""
# Merge Conflict Resolution Request

**Operation ID:** {conflict_report.operation_id}
**Timestamp:** {conflict_report.timestamp.isoformat()}
**Conflicted Files:** {len(conflict_report.conflicted_files)}

## Files Requiring Resolution
"""

        for file_path in conflict_report.conflicted_files:
            details = conflict_report.conflict_details.get(file_path, {})
            prompt += (
                f"\n- **{file_path}** "
                f"({details.get('conflict_markers', 0)} conflict markers)"
            )

        prompt += f"""

## Repository State
- Working Directory: {os.getcwd()}
- Current Branch: {self._get_current_branch()}
- State Directory: {state_dir}

## Resolution Instructions
1. Analyze the conflicted files in the state directory
2. Resolve merge conflicts preserving both sets of changes where possible
3. Ensure the resulting code is syntactically correct and functional
4. Test the resolution if applicable
5. Provide a clear explanation of changes made

## Context
The merge conflict occurred during automated repository synchronization.
Please resolve conflicts while maintaining the integrity of both branches.
"""

        return prompt

    def _get_repository_state(self) -> Dict[str, Any]:
        """Get current repository state information."""
        try:
            # Get current branch
            branch = self._get_current_branch()

            # Get last commit
            result = subprocess.run(
                ["git", "log", "-1", "--format=%H|%s|%an|%ad"],
                capture_output=True,
                text=True,
                check=True,
            )

            commit_hash, subject, author, date = result.stdout.strip().split("|")

            # Get working directory status
            status_result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                check=True,
            )

            modified_files = len(
                [
                    line
                    for line in status_result.stdout.strip().split("\n")
                    if line.strip()
                ]
            )

            return {
                "current_branch": branch,
                "last_commit": {
                    "hash": commit_hash,
                    "subject": subject,
                    "author": author,
                    "date": date,
                },
                "working_directory": {
                    "modified_files": modified_files,
                    "is_clean": modified_files == 0,
                },
            }

        except Exception as e:
            self.logger.error(f"Failed to get repository state: {e}")
            return {"error": str(e)}

    def _get_current_branch(self) -> str:
        """Get current git branch name."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return "unknown"

    def _log_escalation(self, escalation: OpenCodeEscalation):
        """Log escalation event."""
        escalation_data = asdict(escalation)
        escalation_data["timestamp"] = escalation.timestamp.isoformat()

        self.logger.info(
            f"OpenCode escalation: {escalation.operation_id} -> "
            f"{escalation.context_file}"
        )


class MergeResolutionLogger:
    """Handles logging of merge resolution attempts and outcomes."""

    def __init__(self, config=None):
        self.config = config or get_config()
        self.logger = get_logger(f"{__name__}.logger")

    def log_merge_attempt(
        self,
        operation_id: str,
        source_branch: str,
        target_branch: str,
        source_commit: str,
        target_commit: str,
    ):
        """Log a merge attempt."""
        self.logger.info(
            f"Merge attempt: {operation_id} ({source_branch} -> {target_branch})"
        )

        # In a real implementation, this would be stored in a database
        # For now, we'll just log it

    def log_merge_resolution_outcome(
        self,
        operation_id: str,
        conflicts_resolved: int,
        total_conflicts: int,
        resolution_status: MergeResolutionStatus,
    ):
        """Log the outcome of a merge resolution attempt."""
        self.logger.info(
            f"Merge resolution outcome: {operation_id} - "
            f"{conflicts_resolved}/{total_conflicts} conflicts resolved - "
            f"Status: {resolution_status.value}"
        )

    def log_timeout_event(
        self, operation_id: str, timeout_duration: int, event_type: str
    ):
        """Log timeout events during merge operations."""
        self.logger.warning(
            f"Merge timeout event: {operation_id} - "
            f"{event_type} after {timeout_duration} seconds"
        )


# Convenience functions for backward compatibility
def classify_merge_error(exit_code: int, error_output: str) -> MergeErrorType:
    """Classify merge error type."""
    detector = MergeConflictDetector()
    return detector.classify_merge_error(exit_code, error_output)


def log_merge_attempt(
    operation_id: str,
    source_branch: str,
    target_branch: str,
    source_commit: str,
    target_commit: str,
):
    """Log merge attempt."""
    logger = MergeResolutionLogger()
    logger.log_merge_attempt(
        operation_id, source_branch, target_branch, source_commit, target_commit
    )


def log_opencode_escalation(
    operation_id: str, context_file: str, context_data: Dict[str, Any]
):
    """Log OpenCode escalation."""
    escalation = OpenCodeEscalation(
        operation_id=operation_id,
        escalation_type="merge_conflict",
        context_file=context_file,
        context_data=context_data,
        timestamp=datetime.now(),
    )

    # Log the escalation using the escalation engine
    escalation_engine = MergeEscalationEngine()
    escalation_engine._log_escalation(escalation)


def log_merge_resolution_outcome(
    operation_id: str, conflicts_resolved: int, total_conflicts: int, operation: str
):
    """Log merge resolution outcome."""
    logger = MergeResolutionLogger()
    status = (
        MergeResolutionStatus.SUCCESS
        if conflicts_resolved == total_conflicts
        else MergeResolutionStatus.FAILED
    )
    logger.log_merge_resolution_outcome(
        operation_id, conflicts_resolved, total_conflicts, status
    )


def log_timeout_event(operation_id: str, timeout_duration: int, event_type: str):
    """Log timeout event."""
    logger = MergeResolutionLogger()
    logger.log_timeout_event(operation_id, timeout_duration, event_type)
