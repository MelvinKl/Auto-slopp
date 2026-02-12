"""Plugin management system using pluggy."""

from pathlib import Path
from typing import List, Type

import pluggy

from auto_slopp.hooks import hookimpl
from auto_slopp.worker import Worker


class PluginManager:
    """Manages plugins and worker registration using pluggy."""

    def __init__(self):
        """Initialize the plugin manager."""
        self.pm = pluggy.PluginManager("auto_slopp")
        self._register_hookspecs()
        self._load_builtin_plugins()

    def _register_hookspecs(self) -> None:
        """Register hook specifications with the plugin manager."""
        import auto_slopp.hooks as hooks_module

        self.pm.add_hookspecs(hooks_module)

    def _load_builtin_plugins(self) -> None:
        """Load built-in plugins."""
        # Register the builtin worker plugin
        self.pm.register(BuiltinWorkerPlugin(), "builtin_workers")

    def register_plugin(self, plugin, name: str | None = None) -> None:
        """Register a plugin with the manager.

        Args:
            plugin: Plugin object or module
            name: Optional name for the plugin
        """
        if name:
            self.pm.register(plugin, name=name)
        else:
            self.pm.register(plugin)

    def load_plugins_from_path(self, search_path: Path) -> None:
        """Load plugins from a given search path.

        Args:
            search_path: Directory path to search for plugins
        """
        import importlib
        import importlib.util
        import sys

        if not search_path.exists() or not search_path.is_dir():
            return

        # Add search path to sys.path temporarily
        search_path_str = str(search_path.resolve())
        original_path = sys.path[:]

        try:
            if search_path_str not in sys.path:
                sys.path.insert(0, search_path_str)

            # Find all Python files in the search path
            for py_file in search_path.rglob("*.py"):
                if py_file.name.startswith("__"):
                    continue

                try:
                    # Convert file path to module path
                    relative_path = py_file.relative_to(search_path)
                    module_path = relative_path.with_suffix("").as_posix().replace("/", ".")

                    # Import the module
                    spec = importlib.util.spec_from_file_location(module_path, py_file)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)

                        # Register plugin if it has pluggy hook implementations
                        if hasattr(module, "__plugin__") or any(
                            hasattr(getattr(module, attr, None), "auto_slopp_") for attr in dir(module)
                        ):
                            self.pm.register(module, module_path)

                except Exception:
                    # Skip modules that can't be imported
                    continue

        finally:
            # Restore original sys.path
            sys.path[:] = original_path

    def get_registered_workers(self) -> List[Type[Worker]]:
        """Get all registered worker classes from plugins.

        Returns:
            List of worker classes
        """
        workers = []

        # Get workers from plugins that implement the register_workers hook
        for worker_class_list in self.pm.hook.auto_slopp_register_workers():
            workers.extend(worker_class_list)

        return workers

    def get_hook(self) -> pluggy.HookRelay:
        """Get the hook relay for calling plugin hooks.

        Returns:
            Hook relay object
        """
        return self.pm.hook


class BuiltinWorkerPlugin:
    """Built-in plugin that registers workers from the discovery system."""

    def __init__(self):
        """Initialize the builtin plugin."""
        self._discovered_workers: List[Type[Worker]] = []

    def set_discovered_workers(self, workers: List[Type[Worker]]) -> None:
        """Set the discovered workers from the filesystem.

        Args:
            workers: List of discovered worker classes
        """
        self._discovered_workers = workers

    @hookimpl
    def auto_slopp_register_workers(self) -> List[Type[Worker]]:
        """Register discovered workers as plugins.

        Returns:
            List of worker classes
        """
        return self._discovered_workers
