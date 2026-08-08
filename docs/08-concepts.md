# 8 Concepts

## 8.1 TaskSource Abstraction

The `TaskSource` interface decouples task processing logic from task loading logic:

```
┌──────────────────┐
│   IssueWorker    │  ← Unified processing logic
│                  │
│  ┌────────────┐  │
│  │ TaskSource │◀─┘  ← Abstraction layer
│  └─────┬──────┘
│        │
│  ┌─────┴──────┐  ┌──────────────────┐
│  │GitHubTask  │  │ VikunjaTask      │
│  │Source      │  │ Source            │
│  └─────┬──────┘  └────────┬─────────┘
│        │                   │
│        ▼                   ▼
│  ┌──────────┐       ┌──────────┐
│  │ GitHub   │       │ Vikunja  │
│  │ Issues   │       │ Tasks    │
│  └──────────┘       └──────────┘
```

**Key Methods**:
- `get_tasks(repo_path)` → Load and filter tasks
- `get_branch_name(task)` → Generate git branch name
- `on_task_complete()` / `on_task_failure()` → Lifecycle callbacks
- `get_task_difficulty_name()` → Map to CLI tool difficulty rating

## 8.2 Ralph Loop

The Ralph loop is a structured 5-step execution pattern for processing tasks:

```
┌──────────────────────────────────────────────────────┐
│                    Ralph Loop                         │
│                                                       │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐          │
│  │ Analyze │───▶│Implement│───▶│  Test   │          │
│  └─────────┘    └─────────┘    └─────────┘          │
│       ▲                              │               │
│       │         ┌─────────┐          │               │
│       └─────────│Document │◀─────────┘               │
│                 └────┬────┘                          │
│                      │                               │
│                      ▼                               │
│               ┌─────────┐                            │
│               │Validate │                            │
│               │(make     │                            │
│               │ test)   │                            │
│               └────┬────┘                            │
│                    │                                  │
│              ┌─────┴─────┐                            │
│              │           │                            │
│              ▼           ▼                            │
│         ┌─────────┐ ┌─────────┐                      │
│         │Success  │ │Max Iter.│                      │
│         └─────────┘ └─────────┘                      │
└──────────────────────────────────────────────────────┘
```

Each step is represented as a checkbox in a markdown plan file (`.ralph/`). Steps execute sequentially. Completed steps are committed automatically. If the final validation (`make test`) fails, the task file is deleted for a fresh start on next iteration.

## 8.3 Tiered CLI Tool Selection

Auto-slopp defines CLI tool configurations in code as a Pydantic `List[CLIConfiguration]`:

```
Default CLI Configurations:
┌────────────┬──────────┬──────────────────────────────────┐
│ Tool       │ Capability│ Name                          │
├────────────┼──────────┼──────────────────────────────────┤
│ pi         │ 6        │ pi Qwen3.6-35B-A3B             │
│ opencode   │ 7        │ opencode nemotron-3-ultra-free │
│ opencode   │ 8        │ opencode gpt-5                  │
│ opencode   │ 9        │ opencode gpt-5-mini             │
└────────────┴──────────┴──────────────────────────────────┘

Task Difficulty: {min: 0, max: 10, recommended: 10}

Selection: opencode gpt-5-mini (capability 9, closest to recommended 10)
```

**Filtering**: Tools outside `[min_rating, max_rating]` are excluded.
**Ranking**: Tools are sorted by closeness to `recommended_rating` (lower index preferred on tie).
**Cooldown**: Failing tools enter cooldown for `cooldown_seconds` (configurable per tool).
**Health Probe**: All tools are probed on startup; unhealthy ones start in cooldown.
**Blacklisting**: Tools can be blacklisted for specific task types via `blacklist_tasks`.

Task difficulty ratings are defined per-task-type:
- `task_planning`: min=0, max=10, recommended=10
- `implementation`: min=5, max=10, recommended=10
- `task_implementation_validation`: min=0, max=10, recommended=6
- `remaining_steps_update`: min=0, max=10, recommended=4
- `pr_description`: min=0, max=10, recommended=1
- `pr_review`: min=0, max=10, recommended=4
- `git_checkout`: min=0, max=10, recommended=2
- `default`: min=0, max=10, recommended=5

## 8.4 Comment Condensation (GitHub)

When processing GitHub issues, comments from the issue author and a whitelisted user are condensed:

1. Collect comments from `issue.author` and `AUTO_SLOPP_GITHUB_ISSUE_WORKER_ALLOWED_CREATOR`
2. Merge into a single summary comment
3. Delete original comments from those users
4. Post the condensed comment

This keeps issue threads clean while preserving important context.

## 8.5 Branch-per-Task Workflow

Each task gets its own git branch:

```
main ─────────────────────────────────────────────────
                 ├── ai/issue-42-fix-bug ────▶ PR ──▶ merged
                 ├── ai/issue-43-add-feature ─▶ PR ──▶ merged
                 └── ai/vikunja-100-task ────▶ PR ──▶ merged
```

1. Create branch from current `main` state
2. Process task on branch (Ralph loop)
3. If changes exist, create PR via task source
4. Clean up branch after merge

## 8.6 Worker Registration

Workers are registered in a hardcoded list in `executor.py`:

```python
ALL_WORKERS: list[Type[Worker]] = [
    GitHubIssueWorker,
    PRWorker,
    StaleBranchCleanupWorker,
    VikunjaWorker,
    PrReviewWorker,
]
```

**Adding a new worker**:
1. Create a new file in `workers/` (e.g., `jira_worker.py`)
2. Implement the `Worker` base class with `run(repo_path)` method
3. Add the worker class to `ALL_WORKERS` in `executor.py`
4. Import it in `workers/__init__.py`

**Disabling workers**: Set `AUTO_SLOPP_WORKERS_DISABLED` to a comma-separated list of worker class names (e.g., `"StaleBranchCleanupWorker,PrReviewWorker"`).

## 8.7 Logging Architecture

Three logging outputs, all configurable:

```
┌─────────────────────────────────────────────────────┐
│                    Log Records                       │
│                                                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │
│  │  Console │  │   File   │  │   Telegram       │   │
│  │ Handler  │  │ Handler  │  │   Handler        │   │
│  │ All Lvl  │  │ WARNING+ │  │  WARNING+ (async)│   │
│  └──────────┘  └──────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────────┘
```

- **Console**: All log levels, immediate output
- **File**: WARNING and above, rotating (10MB × 5 files), enabled via `AUTO_SLOPP_LOG_FILE_DIR`
- **Telegram**: WARNING and above, async HTTP with retries, enabled via `AUTO_SLOPP_TELEGRAM_ENABLED`
