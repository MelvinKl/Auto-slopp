from pathlib import Path


class Settings:
    """Application settings."""

    def __init__(
        self,
        task_directory: Path | None = None,
        verbose: bool = False,
    ):
        self.task_directory = task_directory or Path.cwd()
        self.verbose = verbose

    @classmethod
    def from_dict(cls, data: dict) -> "Settings":
        """Create settings from dictionary."""
        return cls(
            task_directory=Path(data.get("task_directory", ".")),
            verbose=data.get("verbose", False),
        )

    def to_dict(self) -> dict:
        """Convert settings to dictionary."""
        return {
            "task_directory": str(self.task_directory),
            "verbose": self.verbose,
        }
