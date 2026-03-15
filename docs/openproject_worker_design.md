# OpenProject Worker Design

## Overview

The OpenProject Worker automates task processing by integrating OpenProject (project management) with GitHub repositories. It mirrors the GitHubIssueWorker pattern but sources tasks from OpenProject instead of GitHub Issues.

## Architecture

### Components to Reuse (No Changes Required)

| Component | Module | Purpose |
|-----------|--------|---------|
| Worker base class | `auto_slopp.worker.Worker` | Abstract base for all workers |
| Git operations | `auto_slopp.utils.git_operations` | Branch creation, checkout, push, sanitize |
| GitHub operations | `auto_slopp.utils.github_operations` | PR creation, branch management |
| CLI executor | `auto_slopp.utils.cli_executor` | Execute instructions with CLI tools |
| Ralph loop | `auto_slopp.utils.ralph` | Step-based execution with plans |

### New Components Required

1. **OpenProject API Client** - `src/auto_slopp/utils/openproject_operations.py`
2. **OpenProject Worker** - `src/auto_slopp/workers/openproject_worker.py`
3. **Settings** - Add OpenProject configuration to `src/settings/main.py`

## Workflow

```
For each GitHub repository:
    │
    ├─► Get/corresponding OpenProject project (by name match)
    │   └─► Create project if not exists
    │
    ├─► Get open tasks assigned to configured user
    │
    └─► For first open task:
        │
        ├─► Create subtasks with detailed descriptions
        │
        ├─► Create branch: ai/op-{task_id}-{sanitized_subject}
        │
        ├─► Execute subtasks using Ralph loop
        │   └─► Each subtask is a step in the plan
        │
        ├─► Commit and push changes
        │
        ├─► Create PR in GitHub
        │
        ├─► Add comment to OpenProject task
        │
        └─► Set task status to "in progress"
```

## OpenProject API Client Design

### Required API Endpoints

| Function | Endpoint | Purpose |
|----------|----------|---------|
| `get_projects()` | `/api/v3/projects` | List all projects |
| `get_project_by_name()` | `/api/v3/projects?filters=[{"name":{"operator":"=","values":["name"]}}]` | Find project by name |
| `create_project()` | `/api/v3/projects` | Create new project |
| `get_work_packages()` | `/api/v3/projects/{id}/work_packages` | Get tasks for project |
| `create_work_package()` | `/api/v3/projects/{id}/work_packages` | Create subtask |
| `update_work_package()` | `/api/v3/work_packages/{id}` | Update task status |
| `add_comment()` | `/api/v3/work_packages/{id}/activities` | Add comment to task |
| `get_user()` | `/api/v3/users/{id}` | Get user info |

### Data Structures

```python
# Work Package (Task) from OpenProject
{
    "id": int,
    "subject": str,
    "description": {"raw": str},
    "status": {"id": int, "name": str},
    "assignee": {"id": int, "name": str},
    "project": {"id": int, "name": str},
    "_links": {
        "self": {"href": str},
        "project": {"href": str}
    }
}

# Project from OpenProject
{
    "id": int,
    "name": str,
    "identifier": str,
    "_links": {
        "self": {"href": str}
    }
}
```

## OpenProject Worker Design

### Class Structure

```python
class OpenProjectWorker(Worker):
    def __init__(
        self,
        timeout: int | None = None,
        agent_args: List[str] | None = None,
        dry_run: bool = False,
    ):
        # Initialize similar to GitHubIssueWorker
        
    def run(self, repo_path: Path) -> Dict[str, Any]:
        # Main execution flow
        
    def _get_or_create_project(self, repo_name: str) -> Dict | None:
        # Find or create OpenProject project
        
    def _get_open_tasks_for_user(self, project_id: int) -> List[Dict]:
        # Get open tasks assigned to configured user
        
    def _create_subtasks(self, task: Dict, repo_dir: Path) -> List[Dict]:
        # Generate subtasks based on parent task analysis
        
    def _process_single_task(self, repo_dir: Path, task: Dict) -> Dict[str, Any]:
        # Process one task (create branch, execute, create PR)
        
    def _execute_with_ralph_loop(...) -> Dict[str, Any]:
        # Execute subtasks as Ralph steps
        
    def _build_instructions(...) -> str:
        # Build instructions for CLI executor
```

### Branch Naming Convention

```
ai/op-{task_id}-{sanitized_subject_30_chars}
```

Example: `ai/op-42-implement-user-authentication`

## Settings Configuration

### New Settings Fields

```python
# OpenProject Configuration
openproject_url: str = Field(
    default="",
    description="Base URL for OpenProject instance (e.g., https://openproject.example.com)"
)

openproject_api_token: str = Field(
    default="",
    description="API token for OpenProject authentication"
)

openproject_assigned_user_id: int = Field(
    default=0,
    description="User ID to filter tasks assigned to (auto-slopper user)"
)

openproject_default_status_id: int = Field(
    default=1,
    description="Default status ID for new tasks"
)

openproject_in_progress_status_id: int = Field(
    default=2,
    description="Status ID to set when task is in progress"
)

openproject_project_prefix: str = Field(
    default="",
    description="Optional prefix for project identifiers"
)
```

### Environment Variables

```bash
AUTO_SLOPP_OPENPROJECT_URL=https://openproject.example.com
AUTO_SLOPP_OPENPROJECT_API_TOKEN=your_api_token
AUTO_SLOPP_OPENPROJECT_ASSIGNED_USER_ID=5
AUTO_SLOPP_OPENPROJECT_DEFAULT_STATUS_ID=1
AUTO_SLOPP_OPENPROJECT_IN_PROGRESS_STATUS_ID=2
```

## Subtask Generation Strategy

The worker will analyze the parent task and generate subtasks using the CLI tool with a structured prompt:

```
Analyze this task and create a breakdown of subtasks:
- Task Subject: {subject}
- Task Description: {description}

Generate 3-7 subtasks that:
1. Are specific and actionable
2. Include mention of reusable components from the codebase
3. Follow the standard development workflow
4. Can be executed sequentially

Format each subtask as a clear instruction.
```

## Error Handling

- API failures: Log error, return empty list, continue to next repo
- Project not found: Create project if configured, else skip
- Branch creation failure: Log and skip task
- PR creation failure: Log but continue, update OpenProject anyway
- Ralph loop failure: Log error, don't mark task as in progress

## Testing Strategy

Similar to GitHubIssueWorker tests:
1. Test initialization with various parameters
2. Test with no tasks available
3. Test dry run mode
4. Test branch name sanitization
5. Test error handling scenarios
6. Test subtask generation
7. Mock OpenProject API responses

## Implementation Order

1. Create `openproject_operations.py` with API client
2. Add settings to `main.py`
3. Create `openproject_worker.py`
4. Add worker to `workers/__init__.py`
5. Update `.env.example` with new settings
6. Write tests in `tests/test_openproject_worker.py`
7. Update `README.md` if needed

## Differences from GitHubIssueWorker

| Aspect | GitHubIssueWorker | OpenProjectWorker |
|--------|-------------------|-------------------|
| Task source | GitHub Issues | OpenProject Work Packages |
| Task filter | By label and creator | By assignee and status |
| Branch prefix | `ai/issue-` | `ai/op-` |
| Subtask creation | N/A | Creates subtasks before execution |
| Status update | Close issue | Set to "in progress" |
| Project matching | Repository-based | Name match with OpenProject project |
