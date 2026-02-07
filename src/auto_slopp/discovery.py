"""Worker discovery mechanism for finding and loading Worker subclasses."""

import importlib
import inspect
from pathlib import Path
from typing import List, Optional, Type, TypeVar

from .worker import Worker

T = TypeVar("T", bound=Worker)


def discover_workers(search_path: Path) -> List[Type[Worker]]:
    """Discover all Worker subclasses in the given search path.

    Scans the search_path for Python files and dynamically imports them
    to find all classes that inherit from the Worker base class.

    Args:
        search_path: Directory path to search for worker implementations

    Returns:
        List of Worker subclass types found in the search path
    """
    workers: List[Type[Worker]] = []

    if not search_path.exists() or not search_path.is_dir():
        return workers

    # Find all Python files in the search path
    for py_file in search_path.rglob("*.py"):
        if py_file.name.startswith("__"):
            continue

        try:
            # Convert file path to module path
            module_path = _file_to_module_path(py_file, search_path)
            if not module_path:
                continue

            # Import the module
            module = importlib.import_module(module_path)

            # Find all Worker subclasses in the module
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, Worker) and obj is not Worker and obj.__module__ == module_path:
                    workers.append(obj)

        except (ImportError, SyntaxError, AttributeError) as e:
            # Skip files that can't be imported
            print(f"Warning: Could not import {py_file}: {e}")
            continue

    return workers


def _file_to_module_path(file_path: Path, search_path: Path) -> Optional[str]:
    """Convert a file path to a Python module path.

    Args:
        file_path: Absolute path to the Python file
        search_path: Base search path

    Returns:
        Module path string or None if conversion fails
    """
    try:
        # Get relative path from search_path
        relative_path = file_path.relative_to(search_path)

        # Remove .py extension and convert to module path
        module_path = relative_path.with_suffix("").as_posix().replace("/", ".")

        return module_path
    except ValueError:
        return None
