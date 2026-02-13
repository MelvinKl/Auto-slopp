import os
import sys
from pathlib import Path


def find_task_files(directory: Path) -> list[Path]:
    """Find all .txt task files in the directory."""
    if not directory.exists():
        return []
    return sorted(directory.glob("*.txt"))


def process_task_file(file_path: Path) -> bool:
    """Process a single task file."""
    try:
        content = file_path.read_text()
        return len(content) > 0
    except IOError, OSError:
        return False


def mark_task_used(file_path: Path) -> None:
    """Mark a task file as used by renaming it."""
    used_path = file_path.with_suffix(".txt.used")
    try:
        file_path.rename(used_path)
    except OSError:
        pass


def run(directory: Path | None = None) -> int:
    """Main entry point for the auto-slopp processor."""
    if directory is None:
        directory = Path.cwd()

    task_files = find_task_files(directory)
    processed = 0

    for task_file in task_files:
        if process_task_file(task_file):
            processed += 1

    return processed


def main() -> int:
    """Console script entry point."""
    return run()
