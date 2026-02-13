"""Worker discovery mechanism for finding and loading Worker subclasses."""

import importlib
import inspect
from pathlib import Path
from typing import List, Optional, Type, TypeVar

from auto_slopp.worker import Worker

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
    import sys
    import types

    workers: List[Type[Worker]] = []

    if not search_path.exists() or not search_path.is_dir():
        return workers

    # Strategy: Add both the search_path AND the auto_slopp package root to sys.path
    # This allows imports like 'from auto_slopp.worker import Worker' to work
    # regardless of whether search_path is the workers dir or a custom directory

    # Find potential auto_slopp package root by walking up from search_path
    # We look for directories that have 'auto_slopp' as a parent
    search_path_str = str(search_path.resolve())
    original_path = sys.path[:]

    # Collect all paths to add
    paths_to_add = [search_path_str]

    # Try to find and add the auto_slopp package root
    # Check parent directories for 'auto_slopp' folder
    current = search_path.parent
    for _ in range(5):  # Look up to 5 levels
        if current.name == "auto_slopp":
            # Found auto_slopp, add its parent (src) to enable 'auto_slopp.xxx' imports
            package_root = str(current.parent.resolve())
            if package_root not in paths_to_add:
                paths_to_add.insert(0, package_root)
            break
        if current == current.parent:
            break
        current = current.parent

    try:
        # Add all paths to sys.path (at the beginning, priority over installed packages)
        for p in paths_to_add:
            if p not in sys.path:
                sys.path.insert(0, p)

        # Find all Python files in the search path
        for py_file in search_path.rglob("*.py"):
            if py_file.name.startswith("__") and py_file.name != "__init__.py":
                continue

            try:
                # Convert file path to module path
                module_path = _file_to_module_path(py_file, search_path)
                if not module_path and py_file.name != "__init__.py":
                    continue

                # Skip __init__.py at the root of search_path - it's handled differently
                # and trying to import it as a standalone module often fails
                if py_file.name == "__init__.py":
                    relative_dir = py_file.parent.relative_to(search_path)
                    if relative_dir == Path("."):
                        # This is __init__.py at the root of search_path - skip it
                        # The individual worker files will be discovered directly
                        continue
                    # For nested __init__.py, handle as regular module below

                if module_path is None:
                    continue
                module = importlib.import_module(module_path)

                # Find all Worker subclasses in the module
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    module_check = module_path or ""
                    if (
                        issubclass(obj, Worker)
                        and obj is not Worker
                        and obj.__module__.endswith(module_check)
                        and not inspect.isabstract(obj)
                    ):
                        workers.append(obj)

            except (ImportError, SyntaxError, AttributeError) as e:
                # Skip files that can't be imported
                print(f"Warning: Could not import {py_file}: {e}")
                continue

    finally:
        # Restore original sys.path
        sys.path[:] = original_path

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

        # Handle __init__.py files - they represent the package itself
        if module_path == "__init__":
            module_path = ""

        return module_path
    except ValueError:
        return None
