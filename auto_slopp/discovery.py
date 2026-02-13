from importlib import import_module
from pathlib import Path
from sys import modules

from auto_slopp.worker import Worker


def discover_workers(search_path: Path) -> list[type[Worker]]:
    """Discover worker classes in the given search path.

    Args:
        search_path: Path to search for worker modules.

    Returns:
        List of Worker subclasses found.
    """
    if not search_path.exists():
        return []

    workers = []
    for file_path in search_path.glob("*_worker.py"):
        module_name = file_path.stem
        full_name = f"auto_slopp.workers.{module_name}"
        if full_name in modules:
            try:
                module = import_module(full_name)
                worker_class = getattr(module, "TaskProcessorWorker", None)
                if worker_class is not None:
                    workers.append(worker_class)
            except ImportError, AttributeError:
                pass

    return workers


def get_worker_by_name(name: str, workers: list[type[Worker]]) -> type[Worker] | None:
    """Get a worker class by name.

    Args:
        name: Worker name to search for.
        workers: List of worker classes to search in.

    Returns:
        Worker class if found, None otherwise.
    """
    for worker in workers:
        if getattr(worker, "name", None) == name:
            return worker
    return None
