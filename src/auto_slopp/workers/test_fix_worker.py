"""OpenAgent worker implementation for fixing failing tests.

This concrete implementation of OpenAgentWorker provides the specific
instructions for fixing test failures in repositories.
"""

from typing import List

from auto_slopp.base.openagent_worker import OpenAgentWorker


class TestFixWorker(OpenAgentWorker):
    """Concrete OpenAgent worker for fixing failing tests.

    This worker uses OpenAgent to analyze and fix test failures
    in repository code, providing specific instructions for
    test-related fixes.
    """

    def __init__(self, timeout: int = 600, **kwargs):
        """Initialize the TestFixWorker.

        Args:
            timeout: Timeout for OpenAgent execution in seconds
            **kwargs: Additional arguments passed to OpenAgentWorker
        """
        super().__init__(
            agent_args=["fix", "the", "tests", "and", "push", "the", "changes"],
            timeout=timeout,
            capture_output=True,
            process_all_repos=False,
            **kwargs,
        )

    def get_agent_instructions(self) -> str:
        """Get the specific instructions for fixing tests.

        Returns:
            Instructions for OpenAgent to fix failing tests.
        """
        return (
            "You are fixing failing tests in this repository. "
            "Analyze the test failures, identify the root causes, "
            "and implement the necessary fixes to make all tests pass. "
            "Focus on maintaining code quality and following existing patterns. "
            "After fixing the tests, ensure the changes are committed and pushed."
        )
