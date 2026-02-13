"""Console script entry point for nodeenv."""

import argparse
import json
import sys
from pathlib import Path

from auto_slopp.workers.nodeenv_worker import NodeenvWorker


def main() -> int:
    """Main entry point for the nodeenv console script.

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    parser = argparse.ArgumentParser(description="Create Node.js virtual environments")
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
        help="Force recreation of existing environment",
    )
    parser.add_argument(
        "--repo-path",
        type=Path,
        default=Path.cwd(),
        help="Repository directory path",
    )
    parser.add_argument(
        "--output-json",
        action="store_true",
        help="Output result as JSON",
    )

    args = parser.parse_args()

    worker = NodeenvWorker(
        node_version=args.node_version,
        npm_version=args.npm_version,
        env_name=args.env_name,
        force_recreate=args.force,
    )

    task_path = Path.cwd() / args.env_name

    try:
        result = worker.run(args.repo_path, task_path)

        if args.output_json:
            print(json.dumps(result, indent=2))
        else:
            if result.get("success"):
                print(f"Node.js environment created successfully at: {result.get('env_dir')}")
                print(f"Node version: {result.get('node_version')}")
                if result.get("node_installed", {}).get("npm_version"):
                    print(f"npm version: {result.get('node_installed', {}).get('npm_version')}")
            else:
                print(
                    f"Failed to create environment: {result.get('error')}",
                    file=sys.stderr,
                )
                return 1

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
