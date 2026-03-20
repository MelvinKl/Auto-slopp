"""File processing utilities for workers.

This module provides pure functions for common file operations
used across different workers.
"""

import logging
import re
from pathlib import Path
from typing import List, Optional

from auto_slopp.utils.exception_handling import safe_execute

logger = logging.getLogger(__name__)


def find_text_files(directory: Path) -> List[Path]:
    """Find all .txt files in a directory recursively.

    Args:
        directory: Directory to search for .txt files

    Returns:
        List of paths to .txt files, sorted by modification time (oldest first).
    """

    def _find_text_files():
        text_files = []
        for file_path in directory.rglob("*.txt"):
            if file_path.is_file():
                text_files.append(file_path)

        # Sort by modification time (oldest first)
        text_files.sort(key=lambda f: f.stat().st_mtime)

        logger.info(f"Found {len(text_files)} .txt files in {directory.name}")
        return text_files

    result = safe_execute(_find_text_files, default=[], log_errors=True)
    return result if result is not None else []


def read_file_content(file_path: Path) -> Optional[str]:
    """Read content from a text file.

    Args:
        file_path: Path to the file to read

    Returns:
        File content as string, or None if reading failed.
    """

    def _read_file_content():
        content = file_path.read_text(encoding="utf-8").strip()
        if not content:
            logger.warning(f"File is empty: {file_path}")
            return None
        return content

    return safe_execute(_read_file_content, default=None, log_errors=True)


def get_next_counter(directory: Path, counter_start: int = 1) -> int:
    """Get the next available 4-digit counter for file naming.

    Args:
        directory: Directory to search for existing counters
        counter_start: Starting number for counter sequence

    Returns:
        Next available counter number.
    """

    def _get_next_counter():
        # Find all files with counter prefix pattern
        counter_pattern = re.compile(r"^(\d{4})_.*\.used$")
        existing_counters = []

        for file_path in directory.iterdir():
            if file_path.is_file():
                match = counter_pattern.match(file_path.name)
                if match:
                    existing_counters.append(int(match.group(1)))

        # Find next available counter
        if existing_counters:
            max_counter = max(existing_counters)
            return max(counter_start, max_counter + 1)
        else:
            return counter_start

    result = safe_execute(_get_next_counter, default=counter_start, log_errors=True)
    return result if result is not None else counter_start


def rename_processed_file(original_file: Path, counter_start: int = 1) -> Optional[Path]:
    """Rename a processed file with 4-digit counter and .used suffix.

    Args:
        original_file: Path to the original file
        counter_start: Starting number for counter sequence

    Returns:
        Path to the renamed file, or None if renaming failed.
    """
    try:
        # Find next available counter
        counter = get_next_counter(original_file.parent, counter_start)
        counter_str = f"{counter:04d}"

        # Create new filename: counter_original_name.used
        new_name = f"{counter_str}_{original_file.stem}.used"
        new_path = original_file.parent / new_name

        # Rename the file
        original_file.rename(new_path)

        logger.info(f"Renamed {original_file.name} to {new_name}")
        return new_path

    except Exception as e:
        logger.error(f"Error renaming file {original_file.name}: {str(e)}")
        return None


def ensure_directory_exists(directory: Path) -> bool:
    """Ensure a directory exists, creating it if necessary.

    Args:
        directory: Directory path to ensure exists

    Returns:
        True if directory exists (was created or already existed), False otherwise.
    """
    try:
        directory.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Failed to ensure directory exists {directory}: {str(e)}")
        return False


def write_temp_instruction_file(work_dir: Path, instructions: str) -> Path:
    """Write instructions to a temporary file.

    Args:
        work_dir: Working directory for the temporary file
        instructions: Instructions content to write

    Returns:
        Path to the created temporary file.

    Raises:
        IOError: If file writing fails
    """
    instruction_file = work_dir / ".agent_instructions.txt"
    instruction_file.write_text(instructions, encoding="utf-8")
    return instruction_file


def cleanup_temp_file(file_path: Path) -> None:
    """Clean up a temporary file safely.

    Args:
        file_path: Path to the temporary file to remove
    """
    try:
        file_path.unlink(missing_ok=True)
    except Exception:
        # Ignore cleanup errors
        pass


def create_file_counter_name(original_file: Path, counter: int) -> str:
    """Create a new filename with counter prefix and .used suffix.

    Args:
        original_file: Original file path
        counter: Counter number to use

    Returns:
        New filename with counter and .used suffix.
    """
    counter_str = f"{counter:04d}"
    return f"{counter_str}_{original_file.stem}.used"
