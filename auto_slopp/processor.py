from pathlib import Path


class Processor:
    """Task file processor."""

    def __init__(self, directory: Path):
        self.directory = directory

    def get_pending_tasks(self) -> list[Path]:
        """Get all pending task files."""
        if not self.directory.exists():
            return []
        return sorted(self.directory.glob("*.txt"))

    def get_completed_tasks(self) -> list[Path]:
        """Get all completed task files."""
        if not self.directory.exists():
            return []
        return sorted(self.directory.glob("*.txt.used"))

    def process(self) -> int:
        """Process all pending tasks."""
        count = 0
        for task_file in self.get_pending_tasks():
            count += 1
        return count

    def count_pending(self) -> int:
        """Return count of pending tasks."""
        return len(self.get_pending_tasks())

    def count_completed(self) -> int:
        """Return count of completed tasks."""
        return len(self.get_completed_tasks())
