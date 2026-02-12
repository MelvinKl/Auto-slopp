"""Worker discovery mechanism using pluggy plugin system."""

import importlib
import inspect
from pathlib import Path
from typing import List, Optional, Type, TypeVar

from auto_slopp.plugin_manager import PluginManager
from auto_slopp.worker import Worker

T = TypeVar("T", bound=Worker)


def discover_workers(search_path: Path) -> List[Type[Worker]]:
    """Discover all Worker subclasses in the given search path using plugin system.

    Uses the pluggy plugin system to discover and register workers from both
    filesystem scanning and plugin registrations.

    Args:
        search_path: Directory path to search for worker implementations

    Returns:
        List of Worker subclass types found in the search path and plugins
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

    # Apply plugin filtering
    plugin_manager = PluginManager()
    plugin_manager.load_plugins_from_path(search_path)

    # Set discovered workers in builtin plugin
    try:
        builtin_plugin = plugin_manager.pm.get_plugin("builtin_workers")
        if builtin_plugin:
            builtin_plugin.set_discovered_workers(workers)
    except Exception:
        # If we can't get the builtin plugin, continue without it
        pass

    # Get all registered workers (including filtered ones)
    registered_workers = plugin_manager.get_registered_workers()

    # Apply filtering hooks if any
    try:
        filtered_workers_list = plugin_manager.get_hook().auto_slopp_filter_workers(workers=registered_workers)
        if filtered_workers_list:
            # Use the last non-empty result from filters
            for filtered in reversed(filtered_workers_list):
                if filtered is not None:
                    workers = filtered
                    break
    except Exception:
        # If filtering fails, use the original list
        pass

    return workers


def get_plugin_manager(search_path: Path) -> PluginManager:
    """Get a plugin manager with workers loaded from the search path.

    Args:
        search_path: Directory path to search for worker implementations

    Returns:
        Configured plugin manager
    """
    plugin_manager = PluginManager()
    plugin_manager.load_plugins_from_path(search_path)

    # Load discovered workers into the builtin plugin
    workers = _discover_workers_raw(search_path)
    try:
        builtin_plugin = plugin_manager.pm.get_plugin("builtin_workers")
        if builtin_plugin:
            builtin_plugin.set_discovered_workers(workers)
    except Exception:
        # If we can't get the builtin plugin, continue without it
        pass

    return plugin_manager


def _discover_workers_raw(search_path: Path) -> List[Type[Worker]]:
    """Discover workers without plugin filtering (internal helper).

    Args:
        search_path: Directory path to search for worker implementations

    Returns:
        List of Worker subclass types found in the search path
    """
    import sys

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

            except ImportError, SyntaxError, AttributeError:
                # Skip files that can't be imported
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
