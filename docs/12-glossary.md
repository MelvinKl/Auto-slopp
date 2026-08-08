# 12 Glossary

| Term | Definition |
|------|-----------|
| **Auto-slopp** | Python-based automation framework for task execution with pluggable worker system |
| **AI-generated code / Slop** | Code produced by AI models that may be plausible-looking but incorrect or unreliable |
| **Branch-per-task** | Workflow where each task gets its own git branch for isolated processing |
| **CLI Tool** | External command-line AI coding tools (opencode, gemini, codex) used for task execution |
| **Comment Condensation** | Merging multiple comments from specific users into a single summary comment |
| **Cooldown** | Period during which a failing CLI tool is excluded from selection |
| **Executor** | Component that discovers and runs worker implementations |
| **GitHub Issue** | A task tracked in GitHub's issue tracker |
| **IssueWorker** | Unified worker that processes tasks from any TaskSource using the Ralph loop |
| **make test** | Makefile target that runs all quality checks: black, isort, flake8, safety, bandit, pytest |
| **Pydantic** | Python library for data validation using type hints (BaseSettings for configuration) |
| **PR (Pull Request)** | A GitHub feature for proposing changes to a repository |
| **PrReviewWorker** | Worker that reviews PRs with the "AI" label and provides conventional comments |
| **PRWorker** | Worker that tests open PR branches and fixes failing tests |
| **Ralph Loop** | Structured 5-step task execution pattern: Analyze → Implement → Test → Document → Validate |
| **Repo Path** | Directory containing git repositories to be managed (`AUTO_SLOPP_BASE_REPO_PATH`) |
| **StaleBranchCleanupWorker** | Worker that removes local branches not on remote and older than threshold |
| **TaskSource** | Abstraction for loading tasks from different sources (GitHub, Vikunja) |
| **Vikunja** | Open-source task management application |
| **VikunjaTaskSource** | TaskSource implementation that loads tasks from Vikunja |
| **VikunjaWorker** | Worker that processes Vikunja tasks using the IssueWorker + VikunjaTaskSource |
| **Worker** | Pluggable automation unit that inherits from `Worker` base class and implements `run()` |
| **Worker Discovery** | Runtime scanning of `workers/` package for `Worker` subclasses |
| **`gh` CLI** | GitHub's official command-line tool for interacting with the GitHub API |
