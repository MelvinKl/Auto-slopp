# 5 Building Block View

## 5.1 Top-Level Decomposition

```
Auto-slopp
├── CLI Entry Point (main.py)
│   ├── Argument parsing
│   ├── Settings loading
│   ├── Logging setup
│   └── Executor invocation
│
├── Executor (executor.py)
│   ├── Worker discovery
│   ├── Worker execution
│   └── Result aggregation
│
├── Worker System
│   ├── Base Worker (worker.py)
│   ├── Unified IssueWorker (issue_worker.py)
│   ├── GitHubIssueWorker (github_issue_worker.py)
│   ├── VikunjaWorker (vikunja_worker.py)
│   ├── PRWorker (pr_worker.py)
│   ├── PRReviewWorker (pr_review_worker.py)
│   └── StaleBranchCleanupWorker (stale_branch_cleanup_worker.py)
│
├── Task Sources
│   ├── TaskSource (abstract base)
│   ├── GitHubTaskSource (github_task_source.py)
│   └── VikunjaTaskSource (vikunja_task_source.py)
│
├── Utilities
│   ├── Git Operations (git_operations.py)
│   ├── GitHub Operations (github_operations.py)
│   ├── Branch Analysis (branch_analysis.py)
│   ├── File Operations (file_operations.py)
│   ├── Repository Utils (repository_utils.py)
│   ├── CLI Executor (cli_executor.py)
│   ├── Ralph Loop (ralph.py)
│   ├── Logging Utils (logging_util.py)
│   └── Vikunja Operations (vikunja_operations.py)
│
├── Settings (settings/main.py)
│   └── Pydantic configuration model
│
└── Telegram Handler (telegram_handler.py)
    └── Async logging to Telegram
```

## 5.2 Component Interfaces

### Worker Interface

```python
class Worker(ABC):
    """Abstract base class for all worker implementations."""
    
    @abstractmethod
    def run(self, repo_path: Path) -> Any:
        """Execute the worker's automation task."""
```

### TaskSource Interface

```python
class TaskSource(ABC):
    """Abstract base class for loading tasks from different sources."""

    def get_tasks(self, repo_path: Path) -> List[Task]: ...
    def get_branch_name(self, task: Task) -> str: ...
    def get_ralph_file_prefix(self) -> str: ...
    def get_pr_title(self, task: Task) -> str: ...
    def get_default_pr_body(self, task: Task) -> str: ...
    def on_task_start(self, task: Task, branch_name: str) -> None: ...
    def on_task_complete(self, task: Task, branch_name: str, pr_url: str, findings: Optional[List[str]] = None) -> None: ...
    def on_task_failure(self, task: Task, error: str) -> None: ...
    def on_no_changes(self, task: Task) -> None: ...
    def on_skip(self, task: Task) -> None: ...
    def on_max_iterations_reached(self, task: Task, steps_completed: int, total_steps: int, error: str) -> None: ...
```

### Executor Interface

```python
class Executor:
    def discover_workers(self) -> List[Type[Worker]]: ...
    def execute_workers(self, repo_path: Path) -> Dict[str, Any]: ...
```

## 5.3 Component Details

### Main (`main.py`)

Entry point that orchestrates initialization:
1. Parse CLI arguments (`--repo-path`, `--debug`)
2. Load settings from environment
3. Set up logging (console + optional Telegram + optional file)
4. Create and run executor

### Executor (`executor.py`)

Manages the worker lifecycle:
1. Uses a hardcoded list of workers (`ALL_WORKERS`) in `executor.py` — no dynamic discovery
2. Filters out disabled workers via `AUTO_SLOPP_WORKERS_DISABLED` setting (list of class names)
3. Instantiates each enabled worker (with special handling for `StaleBranchCleanupWorker` which needs `days_threshold`)
4. Calls `run(repo_path)` on each worker for every subdirectory in `base_repo_path`
5. Handles exceptions per-worker (one failure doesn't stop others)
6. Runs in an endless loop with configurable sleep interval (`AUTO_SLOPP_EXECUTOR_SLEEP_INTERVAL`)
7. Checks for git updates (`git pull`) and can auto-reboot after configurable delay

### IssueWorker (`workers/issue_worker.py`)

Unified task processor:
1. Gets tasks from `task_source.get_tasks()`
2. For each task: creates branch, runs Ralph loop, creates PR
3. Handles task lifecycle callbacks via `task_source`

### Ralph Loop (`utils/ralph.py`)

Structured 5-step task execution:
1. **Analyze** — Identify affected files and expected behavior
2. **Implement** — Apply code changes via CLI tool
3. **Test** — Update or add tests
4. **Document** — Update documentation if needed
5. **Validate** — Run `make test` and confirm success

### Tiered CLI Executor (`utils/cli_executor.py`)

Selects and executes CLI tools:
1. Uses `settings.cli_configurations` (Pydantic model, not JSON env var)
2. Filters tools by task difficulty range (min/max rating from `task_difficulties`)
3. Prefers tools closest to recommended rating
4. Handles cooldown for failing tools (configurable per-tool)
5. Probes tool health on startup via `_check_startup_health()`
6. Maintains per-tool cooldown state to avoid repeated failures

## 5.4 Data Flow

```
Settings → Main → Executor → Workers → TaskSources → External APIs
                                    ↓
                              Managed Repositories
                                    ↓
                              Git Operations
                                    ↓
                              CLI Tools (AI execution)
```
