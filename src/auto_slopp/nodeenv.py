"""Nodeenv command line entry point."""

import argparse
import logging
import sys
from pathlib import Path


def main() -> None:
    """Main entry point for nodeenv command."""
    parser = argparse.ArgumentParser(
        description="Create Node.js virtual environments",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--node-version",
        type=str,
        help="Specific Node.js version to install (e.g., '18.17.0')",
    )
    parser.add_argument(
        "--npm-version",
        type=str,
        help="Specific npm version to install (e.g., '9.6.7')",
    )
    parser.add_argument(
        "--env-name",
        type=str,
        default="nodeenv",
        help="Name for the virtual environment (default: nodeenv)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force recreate existing environment",
    )
    parser.add_argument(
        "path",
        nargs="?",
        type=Path,
        default=Path.cwd(),
        help="Path where to create the environment (default: current directory)",
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger("nodeenv")

    logger.info(f"Creating Node.js environment in: {args.path}")
    logger.info(f"Environment name: {args.env_name}")
    logger.info(f"Node.js version: {args.node_version or 'latest LTS'}")
    logger.info(f"npm version: {args.npm_version or 'latest'}")
    logger.info(f"Force recreate: {args.force}")

    print("Nodeenv command configured:")
    print(f"  Path: {args.path}")
    print(f"  Environment name: {args.env_name}")
    print(f"  Node.js version: {args.node_version or 'latest LTS'}")
    print(f"  npm version: {args.npm_version or 'latest'}")
    print(f"  Force recreate: {args.force}")

    print("\nNote: NodeenvWorker implementation required for actual environment creation.")


if __name__ == "__main__":
    main()
