"""Main entry point for Auto-slopp."""

import argparse
import logging
import sys
from pathlib import Path

from auto_slopp.executor import run_executor
from auto_slopp.telegram_handler import setup_telegram_logging
from settings.main import settings


def setup_logging() -> None:
    """Set up application logging with optional Telegram integration."""
    log_level = logging.DEBUG if settings.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    telegram_handler = setup_telegram_logging(level=log_level)
    if telegram_handler:
        logger = logging.getLogger("auto_slopp")
        logger.addHandler(telegram_handler)
        logger.info("Telegram logging integration enabled")

    logging.getLogger("httpx").setLevel(logging.WARNING)


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments.

    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        description="Auto-slopp - Automation framework for task execution",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  auto-slopp                                    # Use settings defaults
  auto-slopp --repo-path /path/to/repo          # Custom repository path
  auto-slopp --debug                            # Enable debug mode
        """,
    )

    parser.add_argument(
        "--repo-path",
        type=Path,
        help="Path to the repository directory (overrides AUTO_SLOPP_BASE_REPO_PATH)",
    )

    parser.add_argument(
        "--search-path",
        type=Path,
        help="Path to search for worker implementations (overrides AUTO_SLOPP_WORKER_SEARCH_PATH)",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode with verbose logging (overrides AUTO_SLOPP_DEBUG)",
    )

    parser.add_argument("--version", action="version", version="Auto-slopp 0.1.0")

    return parser.parse_args()


def main() -> None:
    """Main entry point for Auto-slopp."""
    args = parse_arguments()

    repo_path = args.repo_path or settings.base_repo_path
    search_path = args.search_path or settings.worker_search_path
    debug = args.debug or settings.debug

    setup_logging()
    logger = logging.getLogger("auto_slopp")

    logger.info("Auto-slopp starting...")
    logger.info(f"Repository path: {repo_path}")
    logger.info(f"Search path: {search_path}")
    logger.info(f"Debug mode: {debug}")
    logger.info(f"Telegram logging: {'enabled' if settings.telegram_enabled else 'disabled'}")

    if debug:
        logger.debug("Debug mode enabled - showing detailed logs")

    try:
        run_executor(search_path=search_path, repo_path=repo_path)
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
