"""Simple task file processor for Auto-slopp."""

import shutil
from pathlib import Path


class TaskProcessor:
    """Process task files by renaming them with .used suffix."""

    def __init__(self, task_dir: str = "."):
        """Initialize TaskProcessor with a task directory.

        Args:
            task_dir: Directory containing task files to process.
        """
        self.task_dir = Path(task_dir)

    def find_task_files(self) -> list[Path]:
        """Find all .txt files in the task directory.

        Returns:
            Sorted list of Path objects for .txt files.
        """
        return sorted(self.task_dir.glob("*.txt"))

    def process_file(self, filepath: Path) -> bool:
        """Process a single task file by renaming it with .used suffix.

        Args:
            filepath: Path to the task file to process.

        Returns:
            True if file was processed successfully, False otherwise.
        """
        if filepath.suffix == ".used":
            return False
        new_path = filepath.with_suffix(".txt.used")
        try:
            shutil.move(str(filepath), str(new_path))
            return True
        except OSError:
            return False

    def process_all(self) -> int:
        """Process all task files in the task directory.

        Returns:
            Number of files processed.
        """
        count = 0
        for filepath in self.find_task_files():
            if self.process_file(filepath):
                count += 1
        return count


def main():
    """Main entry point for the task processor."""
    processor = TaskProcessor()
    count = processor.process_all()
    print(f"Processed {count} task file(s)")


if __name__ == "__main__":
    main()
