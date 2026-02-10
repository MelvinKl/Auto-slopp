#!/usr/bin/env python3
"""Example usage of the TaskProcessorWorker.

This example demonstrates how to use the TaskProcessorWorker to process
text files containing instructions and execute them with OpenCode.
"""

import logging
from pathlib import Path

# Set up logging to see worker activity
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

from auto_slopp.workers import TaskProcessorWorker


def main():
    """Run TaskProcessorWorker example."""
    # Define paths
    repo_path = Path("/path/to/repositories")  # Directory containing repositories
    task_repo_path = Path("/path/to/task_repos")  # Directory for task repositories

    # Initialize the worker
    worker = TaskProcessorWorker(
        task_repo_path=task_repo_path,
        counter_start=1,  # Start counting from 0001
        timeout=300,  # 5 minutes timeout for OpenCode
        agent_args=["--verbose"],  # Additional OpenCode arguments
        dry_run=True,  # Set to False for actual execution
    )

    print(f"TaskProcessorWorker initialized")
    print(f"Repository path: {repo_path}")
    print(f"Task repository path: {task_repo_path}")
    print(f"Dry run mode: {worker.dry_run}")
    print()

    # Run the worker
    result = worker.run(repo_path, Path("/tmp/dummy_task_path"))

    # Print results
    print("\n=== TaskProcessorWorker Results ===")
    print(f"Success: {result['success']}")
    print(f"Repositories processed: {result['repositories_processed']}")
    print(f"Repositories with errors: {result['repositories_with_errors']}")
    print(f"Text files processed: {result['text_files_processed']}")
    print(f"OpenCode executions: {result['openagent_executions']}")
    print(f"Files renamed: {result['files_renamed']}")
    print(f"Git operations: {result['git_operations']}")
    print(f"Execution time: {result['execution_time']:.2f} seconds")

    # Print repository-specific results
    if result["repository_results"]:
        print("\n=== Repository Details ===")
        for repo_result in result["repository_results"]:
            print(f"\nRepository: {repo_result['repository']}")
            print(f"  Success: {repo_result['success']}")
            print(
                f"  Text files processed: {repo_result.get('text_files_processed', 0)}"
            )
            print(f"  Files renamed: {repo_result.get('files_renamed', 0)}")

            if repo_result.get("errors"):
                print(f"  Errors: {', '.join(repo_result['errors'])}")

            if repo_result.get("processed_files"):
                print(f"  Processed files:")
                for file_result in repo_result["processed_files"]:
                    print(f"    {file_result['file']}: {file_result['success']}")


if __name__ == "__main__":
    main()
