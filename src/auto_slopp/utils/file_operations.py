"""File processing utilities for workers.

This module provides pure functions for common file operations
used across different workers.
"""

import logging
import re
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


def get_next_counter(directory: Path, counter_start: int = 1) -> int:
    """Get the next available 4-digit counter for file naming.

    Args:
        directory: Directory to search for existing counters
        counter_start: Starting number for counter sequence

    Returns:
        Next available counter number.
    """
    try:
        # Find all files with counter prefix pattern
        counter_pattern = re.compile(r"^(\d{4})_.*\.used$")
        existing_counters = []

        for file_path in directory.iterdir():
            if file_path.is_file():
                match = counter_pattern.match(file_path.name)
                if match:
                    existing_counters.append(int(match.group(1)))

        # Find next available counter
        if existing_counters:
            max_counter = max(existing_counters)
            return max(counter_start, max_counter + 1)
        else:
            return counter_start

    except Exception:
        return counter_start
