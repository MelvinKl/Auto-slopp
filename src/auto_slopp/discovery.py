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

    # Add the search path to sys.path temporarily
    search_path_str = str(search_path.resolve())
    original_path = sys.path[:]

    try:
        if search_path_str not in sys.path:
            sys.path.insert(0, search_path_str)

        # Find all Python files in the search path
        for py_file in search_path.rglob("*.py"):
            if py_file.name.startswith("__") and py_file.name != "__init__.py":
                continue

            try:
                # Convert file path to module path
                module_path = _file_to_module_path(py_file, search_path)
                if not module_path and py_file.name != "__init__.py":
                    continue

                # Import the module (special handling for __init__.py)
                if py_file.name == "__init__.py":
                    # For __init__.py files, import the parent package
                    relative_dir = py_file.parent.relative_to(search_path)
                    if relative_dir == Path("."):
                        # __init__.py in the root of search_path - use directory name as module
                        module_name = search_path.name
                    else:
                        module_name = str(relative_dir).replace("/", ".")

                    if module_name:
                        module = importlib.import_module(module_name)
                    else:
                        # Skip if we can't determine a module name
                        continue
                else:
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
