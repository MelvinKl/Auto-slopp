#!/usr/bin/env python3
"""Example script demonstrating how to use the RenovateTestWorker.

This script shows how to instantiate and run the RenovateTestWorker
to test renovate branches across multiple repositories.
"""

import logging
from pathlib import Path

from auto_slopp.workers import RenovateTestWorker


def main():
    """Main function demonstrating RenovateTestWorker usage."""
    # Set up logging to see what's happening
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Initialize the worker with custom timeout (optional)
    worker = RenovateTestWorker(timeout=300)  # 5 minutes timeout

    # Define the repository path containing multiple git repositories
    repo_path = Path("/path/to/your/repositories")
    task_path = Path("/tmp/renovate_test_task")  # Not used by this worker

    # Run the worker
    print(f"Starting RenovateTestWorker on: {repo_path}")
    result = worker.run(repo_path, task_path)

    # Display results
    print("\n=== Results ===")
    print(f"Worker: {result['worker_name']}")
    print(f"Success: {result['success']}")
    print(f"Repositories processed: {result['repositories_processed']}")
    print(f"Repositories tested: {result['repositories_tested']}")
    print(f"Repositories fixed: {result['repositories_fixed']}")
    print(f"Repositories with errors: {result['repositories_with_errors']}")

    if result["errors"]:
        print("\nErrors encountered:")
        for error in result["errors"]:
            print(f"  - {error}")

    if result["repository_results"]:
        print("\nRepository details:")
        for repo_result in result["repository_results"]:
            print(f"\nRepository: {repo_result['repository']}")
            print(f"  Success: {repo_result['success']}")
            print(f"  Branches checked out: {repo_result['branches_checked_out']}")

            for test_result in repo_result["test_results"]:
                print(f"  Branch {test_result['branch']}:")
                print(f"    Tests passed: {test_result['success']}")
                if "fix_success" in test_result:
                    print(f"    Fix applied: {test_result['fix_success']}")

            if repo_result["tests_fixed"]:
                print(f"  Tests were fixed in this repository")

    if result["success"]:
        print("\n✅ All operations completed successfully!")
    else:
        print("\n❌ Some operations failed - check the errors above")


if __name__ == "__main__":
    main()
