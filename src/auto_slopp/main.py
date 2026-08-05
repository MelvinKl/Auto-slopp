"""Main entry point for Auto-slopp."""

import argparse
import logging
import sys
from pathlib import Path

from auto_slopp.executor import run_executor
from auto_slopp.telegram_handler import setup_telegram_logging
from auto_slopp.utils.cli_executor import _check_startup_health
from auto_slopp.utils.logging_util import add_file_handler
from settings.main import settings


def setup_logging() -> None:
    """Set up application logging with optional Telegram integration.

    Configures a console stream handler, an optional rotating file handler
    for WARNING+ logs, and an optional Telegram handler.
    """
    log_level = logging.DEBUG if settings.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Get the application logger unconditionally — handlers are added below
    # only when the corresponding settings are enabled.
    logger = logging.getLogger("auto_slopp")

    _add_file_handler_if_configured(logger)
    _add_telegram_handler_if_configured(logger)

    # Reduce noise from third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)


def _add_file_handler_if_configured(logger: logging.Logger) -> None:
    """Add a rotating file handler for WARNING+ logs if configured."""
    if settings.log_file_dir is None:
        return

    log_dir = Path(settings.log_file_dir).expanduser()
    add_file_handler(logger, log_dir=log_dir)


def _add_telegram_handler_if_configured(logger: logging.Logger) -> None:
    """Add a Telegram handler if Telegram logging is enabled."""
    telegram_handler = setup_telegram_logging(level=logging.WARNING)
    if telegram_handler:
        logger.addHandler(telegram_handler)
        logger.info("Telegram logging integration enabled")


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
        "--debug",
        action="store_true",
        help="Enable debug mode with verbose logging (overrides AUTO_SLOPP_DEBUG)",
    )

    parser.add_argument("--version", action="version", version="Auto-slopp 0.1.0")

    parser.add_argument(
        "--no-health-check",
        action="store_true",
        help="Skip startup health check for CLI configurations (useful for CI/debugging)",
    )

    return parser.parse_args()


def main() -> None:
    """Main entry point for Auto-slopp."""
    args = parse_arguments()

    repo_path = args.repo_path or settings.base_repo_path
    debug = args.debug or settings.debug
    no_health_check = bool(args.no_health_check)

    setup_logging()
    logger = logging.getLogger("auto_slopp")

    logger.info("Auto-slopp starting...")
    logger.info(f"Repository path: {repo_path}")
    logger.info(f"Debug mode: {debug}")
    logger.info(f"Telegram logging: {'enabled' if settings.telegram_enabled else 'disabled'}")
    logger.info(f"Startup health check: {'skipped' if no_health_check else 'enabled'}")

    if debug:
        logger.debug("Debug mode enabled - showing detailed logs")

    if not no_health_check:
        _check_startup_health(repo_path)

    try:
        run_executor(repo_path=repo_path)
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
