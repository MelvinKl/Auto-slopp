"""Main entry point for Auto-slopp."""

import sys

from ..settings.main import settings
from .executor import run_executor


def main() -> None:
    """Main entry point for Auto-slopp."""
    print(f"Auto-slopp starting...")
    print(f"Repository path: {settings.base_repo_path}")
    print(f"Task path: {settings.base_task_path}")
    print(f"Search path: {settings.worker_search_path}")
    print(f"Debug mode: {settings.debug}")

    if settings.debug:
        print("Debug mode enabled - showing detailed logs")

    try:
        run_executor()
    except KeyboardInterrupt:
        print("\\nShutdown requested by user")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
