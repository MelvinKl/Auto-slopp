"""
Number State Manager for Auto-slopp.

Provides atomic, concurrent-safe number assignment operations.
Part of the unique number tracking system design.
"""

import json
import os
import fcntl
import time

import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from contextlib import contextmanager
import threading

from ..config import get_config
from ..logging import get_logger


@dataclass
class NumberState:
    """Data structure for number state tracking."""

    used_numbers: List[int]
    last_assigned: int
    created_at: str
    updated_at: str
    context_assignments: Dict[str, int]
    assignments: List[Dict[str, Any]]
    releases: List[Dict[str, Any]]
    metadata: Dict[str, str]
    version: str = "1.0"

    def __post_init__(self):
        if not hasattr(self, "metadata") or self.metadata is None:
            self.metadata = {
                "creator": "number_manager.py",
                "purpose": "unique_number_tracking",
            }


@dataclass
class NumberAssignment:
    """Data structure for number assignment tracking."""

    number: int
    context: str
    assigned_at: str
    assigned_by: str
    description: Optional[str] = None


@dataclass
class NumberRelease:
    """Data structure for number release tracking."""

    number: int
    context: str
    released_at: str
    released_by: str
    reason: Optional[str] = None


class NumberLock:
    """File-based locking mechanism for concurrent access."""

    def __init__(self, lock_file: Path, timeout: int = 30):
        self.lock_file = lock_file
        self.timeout = timeout
        self.logger = get_logger(f"{__name__}.lock")

    def __enter__(self):
        """Enter context manager."""
        if not self._acquire_lock():
            raise TimeoutError(f"Could not acquire lock within {self.timeout} seconds")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        self._release_lock()

    @contextmanager
    def acquire(self):
        """Acquire lock with context manager."""
        if not self._acquire_lock():
            raise TimeoutError(f"Could not acquire lock within {self.timeout} seconds")

        try:
            yield
        finally:
            self._release_lock()

    def _acquire_lock(self) -> bool:
        """Acquire file lock."""
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            try:
                # Create lock file directory if needed
                self.lock_file.parent.mkdir(parents=True, exist_ok=True)

                # Open file and acquire exclusive lock
                self.lock_fd = self.lock_file.open("w")
                fcntl.flock(self.lock_fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

                # Write lock info
                self.lock_fd.write(f"{os.getpid()}\n{datetime.now().isoformat()}\n")
                self.lock_fd.flush()

                self.logger.debug(f"Lock acquired: {self.lock_file}")
                return True

            except (IOError, OSError):
                # Lock is held by someone else, wait and retry
                if hasattr(self, "lock_fd"):
                    self.lock_fd.close()
                time.sleep(0.1)
                continue

        return False

    def _release_lock(self):
        """Release file lock."""
        try:
            if hasattr(self, "lock_fd"):
                fcntl.flock(self.lock_fd.fileno(), fcntl.LOCK_UN)
                self.lock_fd.close()

                # Remove lock file
                if self.lock_file.exists():
                    self.lock_file.unlink()

                self.logger.debug(f"Lock released: {self.lock_file}")

        except Exception as e:
            self.logger.error(f"Error releasing lock: {e}")


class NumberManager:
    """Main number state management class."""

    def __init__(self, config=None, state_dir: Optional[Path] = None):
        self.config = config or get_config()
        self.logger = get_logger(f"{__name__}.manager")

        # Configuration
        if state_dir:
            self.state_dir = state_dir
        else:
            managed_repo_path = Path(self.config.managed_repo_path).expanduser()
            self.state_dir = managed_repo_path / ".number_state"

        self.lock_timeout = 30
        self.max_retries = 5
        self.backup_count = 5

        # Thread-local storage for locks
        self._local_locks = threading.local()

    def init_number_state(self, context_name: str = "default") -> bool:
        """
        Initialize number state directory and files.

        Args:
            context_name: Name of the context to initialize

        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Create state directory structure
            self.state_dir.mkdir(parents=True, exist_ok=True)
            (self.state_dir / "backup").mkdir(exist_ok=True)

            # Create state file if it doesn't exist
            state_file = self.state_dir / "state.json"
            if not state_file.exists():
                initial_state = NumberState(
                    used_numbers=[],
                    last_assigned=0,
                    created_at=datetime.utcnow().isoformat(),
                    updated_at=datetime.utcnow().isoformat(),
                    context_assignments={},
                    assignments=[],
                    releases=[],
                    metadata={
                        "creator": "number_manager.py",
                        "purpose": "unique_number_tracking",
                    },
                )

                self._save_state(initial_state)
                self.logger.info(
                    f"Initialized number state for context: {context_name}"
                )
                return True

            # Validate existing state
            if self.validate_state_file():
                self.logger.info(
                    f"Number state already exists and is valid for context:\n    {context_name}"
                )
                return True
            else:
                self.logger.warning(
                    "Existing state file is invalid, attempting recovery"
                )
                return self.attempt_state_recovery()

        except Exception as e:
            self.logger.error(f"Failed to initialize number state: {e}")
            return False

    def validate_state_file(self) -> bool:
        """
        Validate the state file structure and data.

        Returns:
            True if state file is valid, False otherwise
        """
        try:
            state = self._load_state()

            # Check required fields
            required_fields = [
                "used_numbers",
                "last_assigned",
                "created_at",
                "updated_at",
            ]
            for field in required_fields:
                if not hasattr(state, field):
                    self.logger.error(f"Missing required field: {field}")
                    return False

            # Validate data types
            if not isinstance(state.used_numbers, list):
                self.logger.error("used_numbers must be a list")
                return False

            if not all(isinstance(n, int) for n in state.used_numbers):
                self.logger.error("All used_numbers must be integers")
                return False

            if not isinstance(state.last_assigned, int):
                self.logger.error("last_assigned must be an integer")
                return False

            # Check for duplicates
            if len(state.used_numbers) != len(set(state.used_numbers)):
                self.logger.error("Duplicate numbers found in used_numbers")
                return False

            # Validate context assignments
            if not isinstance(state.context_assignments, dict):
                self.logger.error("context_assignments must be a dictionary")
                return False

            self.logger.debug("State file validation passed")
            return True

        except Exception as e:
            self.logger.error(f"State file validation failed: {e}")
            return False

    def attempt_state_recovery(self) -> bool:
        """
        Attempt to recover state from backups.

        Returns:
            True if recovery successful, False otherwise
        """
        try:
            backup_dir = self.state_dir / "backup"
            if not backup_dir.exists():
                self.logger.error("No backup directory found for recovery")
                return False

            # Find the most recent backup
            backup_files = list(backup_dir.glob("state_*.json"))
            if not backup_files:
                self.logger.error("No backup files found for recovery")
                return False

            # Sort by modification time (most recent first)
            latest_backup = max(backup_files, key=lambda f: f.stat().st_mtime)

            # Load backup state
            with latest_backup.open("r") as f:
                backup_data = json.load(f)

            # Restore backup
            state = NumberState(**backup_data)
            self._save_state(state)

            self.logger.info(f"State recovered from backup: {latest_backup}")
            return True

        except Exception as e:
            self.logger.error(f"State recovery failed: {e}")
            return False

    def get_next_number(
        self, context: str, assigned_by: str, description: Optional[str] = None
    ) -> Optional[int]:
        """
        Get the next available number for a context.

        Args:
            context: Context name for the assignment
            assigned_by: Who is making the assignment
            description: Optional description of the assignment

        Returns:
            Next available number, or None if failed
        """
        lock_file = self.state_dir / "number.lock"

        try:
            with NumberLock(lock_file, self.lock_timeout):
                state = self._load_state()

                # Find next available number
                next_number = self._find_next_available_number(state)

                if next_number is None:
                    self.logger.error("No available numbers found")
                    return None

                # Check if context already has a number assigned
                if context in state.context_assignments:
                    existing_number = state.context_assignments[context]
                    self.logger.warning(
                        f"Context {context} already has number {existing_number}"
                    )
                    return existing_number

                # Assign the number
                state.used_numbers.append(next_number)
                state.last_assigned = next_number
                state.context_assignments[context] = next_number

                # Track assignment
                assignment = NumberAssignment(
                    number=next_number,
                    context=context,
                    assigned_at=datetime.utcnow().isoformat(),
                    assigned_by=assigned_by,
                    description=description,
                )
                state.assignments.append(asdict(assignment))

                # Update timestamp
                state.updated_at = datetime.utcnow().isoformat()

                # Save state
                self._save_state(state)

                # Create backup
                self._create_backup(state)

                self.logger.info(f"Assigned number {next_number} to context {context}")
                return next_number

        except Exception as e:
            self.logger.error(f"Failed to get next number: {e}")
            return None

    def release_number(
        self, context: str, released_by: str, reason: Optional[str] = None
    ) -> bool:
        """
        Release a number from a context.

        Args:
            context: Context name to release
            released_by: Who is releasing the number
            reason: Optional reason for release

        Returns:
            True if release successful, False otherwise
        """
        lock_file = self.state_dir / "number.lock"

        try:
            with NumberLock(lock_file, self.lock_timeout):
                state = self._load_state()

                # Check if context has a number assigned
                if context not in state.context_assignments:
                    self.logger.warning(f"Context {context} has no number assigned")
                    return False

                number = state.context_assignments[context]

                # Remove from used numbers
                if number in state.used_numbers:
                    state.used_numbers.remove(number)

                # Remove from context assignments
                del state.context_assignments[context]

                # Track release
                release = NumberRelease(
                    number=number,
                    context=context,
                    released_at=datetime.utcnow().isoformat(),
                    released_by=released_by,
                    reason=reason,
                )
                state.releases.append(asdict(release))

                # Update timestamp
                state.updated_at = datetime.utcnow().isoformat()

                # Save state
                self._save_state(state)

                # Create backup
                self._create_backup(state)

                self.logger.info(f"Released number {number} from context {context}")
                return True

        except Exception as e:
            self.logger.error(f"Failed to release number: {e}")
            return False

    def get_state_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the current state.

        Returns:
            Dictionary with state statistics
        """
        try:
            state = self._load_state()

            stats = {
                "total_used_numbers": len(state.used_numbers),
                "last_assigned_number": state.last_assigned,
                "available_numbers": self._count_available_numbers(state),
                "active_contexts": len(state.context_assignments),
                "total_assignments": len(state.assignments),
                "total_releases": len(state.releases),
                "state_file_size": (
                    self.state_dir.stat().st_size if self.state_dir.exists() else 0
                ),
                "created_at": state.created_at,
                "updated_at": state.updated_at,
                "version": state.version,
            }

            # Add context assignments
            stats["context_assignments"] = state.context_assignments.copy()

            # Add number gaps if any
            gaps = self.check_number_gaps()
            if gaps:
                stats["number_gaps"] = gaps

            return stats

        except Exception as e:
            self.logger.error(f"Failed to get state stats: {e}")
            return {"error": str(e)}

    def get_context_assignments(self) -> Dict[str, int]:
        """
        Get all current context assignments.

        Returns:
            Dictionary mapping context names to assigned numbers
        """
        try:
            state = self._load_state()
            return state.context_assignments.copy()

        except Exception as e:
            self.logger.error(f"Failed to get context assignments: {e}")
            return {}

    def check_number_gaps(self) -> List[int]:
        """
        Check for gaps in the number sequence.

        Returns:
            List of missing numbers in the sequence
        """
        try:
            state = self._load_state()

            if not state.used_numbers:
                return []

            # Find the expected range
            min_number = min(state.used_numbers)
            max_number = max(state.used_numbers)

            # Find missing numbers
            expected_numbers = set(range(min_number, max_number + 1))
            used_numbers_set = set(state.used_numbers)

            gaps = sorted(expected_numbers - used_numbers_set)

            if gaps:
                self.logger.info(f"Found {len(gaps)} number gaps: {gaps}")

            return gaps

        except Exception as e:
            self.logger.error(f"Failed to check number gaps: {e}")
            return []

    def sync_state_with_files(self, file_patterns: List[str]) -> Dict[str, Any]:
        """
        Sync state with actual files in the filesystem.

        Args:
            file_patterns: List of file patterns to check

        Returns:
            Dictionary with sync results
        """
        results = {
            "files_found": 0,
            "numbers_extracted": 0,
            "orphaned_numbers": 0,
            "missing_numbers": 0,
            "synced": False,
        }

        try:
            # Extract numbers from filenames
            file_numbers = set()
            for pattern in file_patterns:
                for file_path in self.state_dir.parent.glob(pattern):
                    # Try to extract number from filename
                    number = self._extract_number_from_filename(file_path.name)
                    if number is not None:
                        file_numbers.add(number)
                        results["numbers_extracted"] += 1
                    results["files_found"] += 1

            # Get current state
            state = self._load_state()
            state_numbers = set(state.used_numbers)

            # Find orphaned numbers (in state but not in files)
            orphaned = state_numbers - file_numbers
            results["orphaned_numbers"] = len(orphaned)

            # Find missing numbers (in files but not in state)
            missing = file_numbers - state_numbers
            results["missing_numbers"] = len(missing)

            # Update state with missing numbers
            if missing:
                state.used_numbers.extend(list(missing))
                state.used_numbers.sort()
                state.updated_at = datetime.utcnow().isoformat()
                self._save_state(state)
                results["synced"] = True
                self.logger.info(f"Synced {len(missing)} missing numbers into state")

            return results

        except Exception as e:
            self.logger.error(f"Failed to sync state with files: {e}")
            results["error"] = str(e)
            return results

    def cleanup_state(self, max_age_days: int = 90) -> Dict[str, Any]:
        """
        Clean up old state data.

        Args:
            max_age_days: Maximum age for assignments/releases to keep

        Returns:
            Dictionary with cleanup results
        """
        results = {
            "assignments_removed": 0,
            "releases_removed": 0,
            "backups_removed": 0,
            "cleaned": False,
        }

        try:
            state = self._load_state()
            cutoff_date = datetime.utcnow() - timedelta(days=max_age_days)

            # Clean old assignments
            original_count = len(state.assignments)
            state.assignments = [
                assignment
                for assignment in state.assignments
                if datetime.fromisoformat(
                    assignment["assigned_at"].replace("Z", "+00:00")
                )
                > cutoff_date
            ]
            results["assignments_removed"] = original_count - len(state.assignments)

            # Clean old releases
            original_count = len(state.releases)
            state.releases = [
                release
                for release in state.releases
                if datetime.fromisoformat(release["released_at"].replace("Z", "+00:00"))
                > cutoff_date
            ]
            results["releases_removed"] = original_count - len(state.releases)

            # Clean old backups
            backup_dir = self.state_dir / "backup"
            if backup_dir.exists():
                cutoff_timestamp = cutoff_date.timestamp()
                original_count = len(list(backup_dir.glob("state_*.json")))

                for backup_file in backup_dir.glob("state_*.json"):
                    if backup_file.stat().st_mtime < cutoff_timestamp:
                        backup_file.unlink()
                        results["backups_removed"] += 1

            # Save cleaned state
            if (
                results["assignments_removed"] > 0
                or results["releases_removed"] > 0
                or results["backups_removed"] > 0
            ):

                state.updated_at = datetime.utcnow().isoformat()
                self._save_state(state)
                results["cleaned"] = True
                self.logger.info(
                    f"Cleaned up state: removed {results['assignments_removed']} assignments, "
                    f"{results['releases_removed']} releases, {results['backups_removed']} backups"
                )

            return results

        except Exception as e:
            self.logger.error(f"Failed to cleanup state: {e}")
            results["error"] = str(e)
            return results

    # Private helper methods

    def _load_state(self) -> NumberState:
        """Load state from file."""
        state_file = self.state_dir / "state.json"

        if not state_file.exists():
            raise FileNotFoundError(f"State file not found: {state_file}")

        with state_file.open("r") as f:
            data = json.load(f)

        # Ensure metadata field exists
        if "metadata" not in data:
            data["metadata"] = {
                "creator": "number_manager.py",
                "purpose": "unique_number_tracking",
            }

        return NumberState(**data)

    def _save_state(self, state: NumberState):
        """Save state to file."""
        state_file = self.state_dir / "state.json"

        # Create backup before saving
        if state_file.exists():
            backup_file = self.state_dir / "backup" / f"state_{int(time.time())}.json"
            shutil.copy2(state_file, backup_file)

        # Save state
        with state_file.open("w") as f:
            json.dump(asdict(state), f, indent=2)

    def _find_next_available_number(self, state: NumberState) -> Optional[int]:
        """Find the next available number."""
        # Start from last_assigned + 1
        candidate = state.last_assigned + 1

        # Look for the next available number
        while candidate in state.used_numbers:
            candidate += 1

        return candidate

    def _count_available_numbers(self, state: NumberState) -> int:
        """Count available numbers (simplified - assumes infinite range)."""
        # For practical purposes, we'll consider this as the gap count
        gaps = self.check_number_gaps()
        return len(gaps) if gaps else 1  # At least one number should be available

    def _create_backup(self, state: NumberState):
        """Create a backup of the current state."""
        backup_dir = self.state_dir / "backup"
        backup_dir.mkdir(exist_ok=True)

        timestamp = int(time.time())
        backup_file = backup_dir / f"state_{timestamp}.json"

        with backup_file.open("w") as f:
            json.dump(asdict(state), f, indent=2)

        # Clean up old backups (keep only the most recent N)
        backup_files = sorted(
            backup_dir.glob("state_*.json"),
            key=lambda f: f.stat().st_mtime,
            reverse=True,
        )

        for backup_file in backup_files[self.backup_count :]:
            backup_file.unlink()

    def _extract_number_from_filename(self, filename: str) -> Optional[int]:
        """Extract number from filename (basic implementation)."""
        import re

        # Look for patterns like config_123.yaml, test_456.sh, etc.
        match = re.search(r"_(\d+)(?:\.[^.]+)?$", filename)
        if match:
            return int(match.group(1))

        return None


# Global instance
_number_manager: Optional[NumberManager] = None


def get_number_manager(config=None, state_dir: Optional[Path] = None) -> NumberManager:
    """Get the global number manager instance."""
    global _number_manager
    if _number_manager is None:
        _number_manager = NumberManager(config, state_dir)
    return _number_manager


# Convenience functions matching bash script interface
def init_number_state(context_name: str = "default") -> bool:
    """Initialize number state for a context."""
    manager = get_number_manager()
    return manager.init_number_state(context_name)


def get_next_number(
    context: str, assigned_by: str, description: Optional[str] = None
) -> Optional[int]:
    """Get the next available number for a context."""
    manager = get_number_manager()
    return manager.get_next_number(context, assigned_by, description)


def release_number(
    context: str, released_by: str, reason: Optional[str] = None
) -> bool:
    """Release a number from a context."""
    manager = get_number_manager()
    return manager.release_number(context, released_by, reason)


def get_state_stats() -> Dict[str, Any]:
    """Get state statistics."""
    manager = get_number_manager()
    return manager.get_state_stats()
