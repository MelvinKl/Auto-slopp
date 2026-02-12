"""Example plugin demonstrating the pluggy system integration."""

from auto_slopp.hooks import hookimpl
from auto_slopp.worker import Worker


class ExamplePlugin:
    """Example plugin that demonstrates hook implementations."""

    @hookimpl
    def auto_slopp_worker_before_execution(self, worker_class, repo_path, task_path):
        """Called before worker execution."""
        print(f"Example plugin: About to execute {worker_class.__name__}")
        return {"plugin_data": "Example plugin was here"}

    @hookimpl
    def auto_slopp_worker_after_execution(
        self,
        worker_class,
        repo_path,
        task_path,
        result,
        execution_time,
        before_context=None,
    ):
        """Called after worker execution."""
        print(
            f"Example plugin: {worker_class.__name__} completed in {execution_time:.2f}s"
        )
        if before_context and "plugin_data" in before_context:
            print(f"Example plugin: Found context: {before_context['plugin_data']}")

    @hookimpl
    def auto_slopp_modify_worker_kwargs(self, worker_class, kwargs):
        """Modify worker instantiation arguments."""
        # Add a custom parameter to all workers
        if "plugin_modified" not in kwargs:
            kwargs["plugin_modified"] = True
        return kwargs

    @hookimpl
    def auto_slopp_filter_workers(self, workers):
        """Filter workers - remove any worker with 'Test' in the name for demo."""
        filtered = [w for w in workers if "Test" not in w.__name__]
        if len(filtered) != len(workers):
            print(
                f"Example plugin: Filtered out {len(workers) - len(filtered)} test workers"
            )
        return filtered

    @hookimpl
    def auto_slopp_should_execute_worker(self, worker_class, repo_path, task_path):
        """Control worker execution."""
        # Allow all workers to execute for this example
        return None


# Mark this module as a plugin
__plugin__ = True
