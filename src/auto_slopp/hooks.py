"""Hook specifications for the Auto-slopp plugin system."""

from typing import Any, Dict, List, Optional, Type

import pluggy

from auto_slopp.worker import Worker

# Create hook specification markers
hookspec = pluggy.HookspecMarker("auto_slopp")
hookimpl = pluggy.HookimplMarker("auto_slopp")


@hookspec
def auto_slopp_register_workers():
    """Register worker classes with the system.

    Returns:
        List of worker classes to register
    """


@hookspec
def auto_slopp_worker_before_execution(
    worker_class: Type[Worker], repo_path: str, task_path: str
) -> Optional[Dict[str, Any]]:
    """Called before a worker is executed.

    Args:
        worker_class: The worker class being executed
        repo_path: Repository path where worker will run
        task_path: Task path where worker will run

    Returns:
        Optional context data that will be passed to after_execution
    """


@hookspec
def auto_slopp_worker_after_execution(
    worker_class: Type[Worker],
    repo_path: str,
    task_path: str,
    result: Any,
    execution_time: float,
    before_context: Optional[Dict[str, Any]] = None,
) -> None:
    """Called after a worker is executed.

    Args:
        worker_class: The worker class that was executed
        repo_path: Repository path where worker ran
        task_path: Task path where worker ran
        result: The result returned by the worker
        execution_time: Time taken to execute the worker
        before_context: Context data from before_execution hook
    """


@hookspec
def auto_slopp_worker_execution_failed(
    worker_class: Type[Worker],
    repo_path: str,
    task_path: str,
    exception: Exception,
    before_context: Optional[Dict[str, Any]] = None,
) -> None:
    """Called when a worker execution fails.

    Args:
        worker_class: The worker class that failed
        repo_path: Repository path where worker failed
        task_path: Task path where worker failed
        exception: The exception that was raised
        before_context: Context data from before_execution hook
    """


@hookspec
def auto_slopp_modify_worker_kwargs(worker_class: Type[Worker], kwargs: Dict[str, Any]):
    """Modify worker instantiation arguments.

    Args:
        worker_class: The worker class being instantiated
        kwargs: Original arguments for worker instantiation

    Returns:
        Modified arguments dictionary
    """


@hookspec
def auto_slopp_filter_workers(workers: List[Type[Worker]]):
    """Filter the list of discovered workers.

    Args:
        workers: List of all discovered worker classes

    Returns:
        Filtered list of worker classes to execute
    """


@hookspec
def auto_slopp_should_execute_worker(worker_class: Type[Worker], repo_path: str, task_path: str) -> Optional[bool]:
    """Determine if a worker should be executed.

    Args:
        worker_class: The worker class to check
        repo_path: Repository path where worker would run
        task_path: Task path where worker would run

    Returns:
        True if worker should execute, False if not, None to use default behavior
    """
