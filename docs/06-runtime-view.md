# 6 Runtime View

## 6.1 Initialization Sequence

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  Start   │───▶│  Parse   │───▶│  Load    │───▶│  Setup   │───▶│ Discover │
│          │    │  CLI     │    │  Settings│    │  Logging │    │  Workers │
│          │    │  Args    │    │          │    │          │    │          │
└──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
                                                         │
                                                         ▼
                                                    ┌──────────┐
                                                    │  Execute │
                                                    │ Workers  │
                                                    └──────────┘
```

### Detailed Initialization

1. **CLI Parsing**: `argparse` parses `--repo-path`, `--debug`, `--version`
2. **Settings Loading**: Pydantic `Settings` reads `AUTO_SLOPP_*` environment variables
3. **Logging Setup**:
   - Console handler (all levels)
   - File handler (WARNING+, rotating) if `AUTO_SLOPP_LOG_FILE_DIR` is set
   - Telegram handler (WARNING+) if `AUTO_SLOPP_TELEGRAM_ENABLED=true`
4. **Worker Setup**: Use hardcoded `ALL_WORKERS` list from `executor.py` (no dynamic discovery)
5. **Executor Creation**: Initialize `Executor` with `repo_path`

## 6.2 Execution Sequence

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Executor  │────▶│  For Each   │────▶│  Instantiate│
│  execute_   │     │  Worker     │     │  Worker     │
│  workers()  │     │             │     │             │
└─────────────┘     └─────────────┘     └─────────────┘
                           │                    │
                           ▼                    ▼
                    ┌─────────────┐     ┌─────────────┐
                    │  Call       │────▶│  Collect    │
                    │  run()      │     │  Result     │
                    └─────────────┘     └─────────────┘
                           │                    │
                           ▼                    ▼
                    ┌─────────────┐     ┌─────────────┐
                    │  Handle     │◀────│  Aggregate  │
                    │  Exceptions │     │  Results    │
                    └─────────────┘     └─────────────┘
```

### Worker Execution Flow

Each worker's `run(repo_path)` is called independently. Failures in one worker do not stop others.

## 6.3 Task Processing Flow (IssueWorker)

```
┌─────────────────────────────────────────────────────────────────────┐
│                        IssueWorker.run()                            │
│                                                                     │
│  1. task_source.get_tasks(repo_path)                               │
│     └──▶ Filter by labels/tags (e.g., "ai")                       │
│     └──▶ Filter by dependencies                                   │
│                                                                     │
│  2. For each task:                                                 │
│     ├── task_source.on_task_start()                                │
│     ├── Create git branch: task_source.get_branch_name(task)       │
│     ├── Ralph loop (max iterations):                               │
│     │   ├── Analyze step                                           │
│     │   ├── Implement step (via CLI tool)                         │
│     │   ├── Test step                                              │
│     │   ├── Document step                                          │
│     │   └── Validate step (make test)                             │
│     ├── If changes exist: create PR via task_source                │
│     ├── task_source.on_task_complete() / on_task_failure()         │
│     └── Clean up branch                                            │
│                                                                     │
│  3. Return aggregated results                                       │
└─────────────────────────────────────────────────────┬───────────────┘
                                                      │
                                                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         GitHubTaskSource                            │
│  • get_tasks: gh CLI → get_open_issues → filter by label/creator  │
│  • get_branch_name: "ai/issue-<number>-<sanitized-title>"          │
│  • get_pr_title: "#<number>: <title>"                              │
│  • on_task_complete: Close issue, add PR comment, remove label     │
│  • Comment condensation: AI-summarize author comments, delete originals │
│  • on_no_changes: Close issue if no evidence of work               │
│  • on_skip: Generic comment on issue (no error details)            │
│  • on_max_iterations_reached: Comment + remove label (no errors)   │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                         VikunjaTaskSource                           │
│  • get_tasks: Vikunja API → list open tasks with tag "ai"          │
│  • get_branch_name: "ai/vikunja-<task-id>-<sanitized-title>"       │
│  • get_pr_title: "<title>"                                         │
│  • on_task_complete: Update task status via API, create subtasks/PRs │
│  • on_no_changes: Update task status without creating PR           │
│  • on_skip: Update task with skip reason                           │
│  • on_max_iterations_reached: Update task with failure info        │
└─────────────────────────────────────────────────────────────────────┘
```

## 6.4 GitHub Issue Comment Condensation

```
Original Comments              Condensed Result
┌──────────────────┐          ┌──────────────────┐
│ User A: comment 1│          │ Summary comment  │
│ User A: comment 2│ ──────▶  │ (condensed from  │
│ User B: comment 3│          │  User A comments)│
│ User A: comment 4│          │                  │
└──────────────────┘          └──────────────────┘
         │                           │
         ▼                           ▼
   Delete comments 2,4        Replace with summary
   (from allowed_creator)     (from allowed_creator)
```

Only comments from the issue author and `AUTO_SLOPP_GITHUB_ISSUE_WORKER_ALLOWED_CREATOR` are condensed.

## 6.5 CLI Tool Selection Flow

```
Task arrives with difficulty rating
         │
         ▼
┌─────────────────────────┐
│ Filter tools by min/max  │
│ rating range             │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ Sort by closeness to    │
│ recommended rating      │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ Check tool health       │
│ (cooldown status)       │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ Select first healthy    │
│ tool in sorted order    │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ Execute CLI tool with   │
│ task instructions       │
└────────────┬────────────┘
             │
      ┌──────┴──────┐
      │             │
      ▼             ▼
┌──────────┐  ┌──────────┐
│ Success  │  │  Failure │
└────┬─────┘  └────┬─────┘
     │             │
     │             ▼
     │  ┌──────────────────┐
     │  │ Place tool in    │
     │  │ cooldown for     │
     │  │ cooldown_seconds │
     │  └──────────────────┘
     │
     ▼
  Continue to next step
```

## 6.6 Error Handling

```
Exception in worker.run()
         │
         ▼
┌─────────────────┐
│ Log error with  │
│ full context    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Send to Telegram│
│ (if enabled)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Continue with   │
│ next worker     │
│ (don't stop)    │
└─────────────────┘
```

## 6.7 Shutdown

1. Close Telegram HTTP client
2. Flush file log handlers
3. Exit with appropriate code (0 = success, 1 = error)
