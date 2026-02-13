import argparse
import sys
from pathlib import Path

from auto_slopp.processor import Processor
from auto_slopp.settings import Settings


def create_parser() -> argparse.ArgumentParser:
    """Create the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="auto-slopp",
        description="Task file processor for repository automation",
    )
    parser.add_argument(
        "-d",
        "--directory",
        type=Path,
        default=Path.cwd(),
        help="Directory containing task files",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0",
    )
    return parser


def cli() -> int:
    """CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    settings = Settings(
        task_directory=args.directory,
        verbose=args.verbose,
    )

    processor = Processor(settings.task_directory)

    if settings.verbose:
        pending = processor.count_pending()
        completed = processor.count_completed()
        print(f"Pending tasks: {pending}")
        print(f"Completed tasks: {completed}")

    processed = processor.process()
    print(f"Processed {processed} tasks")

    return 0


if __name__ == "__main__":
    sys.exit(cli())
