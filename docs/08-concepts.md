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

Auto-slopp supports multiple AI-powered CLI tools with automatic selection:

```
Task Difficulty: {min: 0, max: 10, recommended: 5}

Available Tools:
┌────────────┬──────────┬──────────────────┐
│ Tool       │ Capability│ Status          │
├────────────┼──────────┼──────────────────┤
│ gemini     │ 8        │ ✓ Healthy       │
│ codex      │ 5        │ ✓ Healthy       │
│ opencode   │ 5        │ ✓ Healthy       │
│ opencode   │ 2        │ ✓ Healthy       │
└────────────┴──────────┴──────────────────┘

Selection: codex (capability 5, closest to recommended 5)
```

**Filtering**: Tools outside `[min_rating, max_rating]` are excluded.
**Ranking**: Tools are sorted by closeness to `recommended_rating`.
**Cooldown**: Failing tools enter cooldown for `cooldown_seconds`.
**Health Probe**: All tools are probed on startup; unhealthy ones start in cooldown.

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

## 8.6 Worker Discovery

Workers are discovered dynamically from the `src/auto_slopp/workers/` package:

1. Scan for Python modules in the workers directory
2. Import each module
3. Find classes that inherit from `Worker` (but are not `Worker` itself)
4. Execute each discovered worker

This allows adding new workers by simply creating a new file in `workers/`.

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
