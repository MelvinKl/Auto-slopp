# OpenProject Worker Specification

## Overview

This specification outlines the required interface and behavior for the OpenProjectWorker, which processes tasks from OpenProject similar to how the GithubIssueWorker processes GitHub issues. The worker follows the same architectural pattern but adapts to OpenProject's API and data model.

## High-Level Functions Required

### 1. Worker Class Structure

```python
class OpenProjectWorker(Worker):
    """Worker for processing OpenProject tasks as instructions.
    
    This worker:
    1. Matches GitHub repositories to OpenProject projects by name
    2. Creates project if it doesn't exist (configurable)
    3. Searches for open tasks assigned to configured user and in ready state
    4. Creates subtasks for implementation steps
    5. Creates a new branch linked to the task
    6. Executes subtasks using the Ralph loop
    7. Commits changes and pushes branch
    8. Creates PR in GitHub
    9. Updates OpenProject task with progress and dependencies
    """
```

### 2. Initialization

The worker must be initialized with the same parameters as GithubIssueWorker:
- `timeout`: Timeout for CLI execution in seconds
- `agent_args`: Additional arguments to pass to the CLI tool
- `dry_run`: If True, skip actual CLI execution and git operations

### 3. Core Workflow Methods

#### 3.1 Main Processing Loop
- `run(repo_path: Path) -> Dict[str, Any]`: Execute the OpenProject task processing workflow for a single repository

#### 3.2 Project Management
- `_is_configured() -> bool`: Check if OpenProject is properly configured
- `_get_or_create_project(repo_name: str) -> Optional[Dict[str, Any]]`: Get or create OpenProject project matching repo name
  - Try to find project by identifier (with prefix)
  - Try to find project by name
  - Create project if not found and auto-creation is enabled
  - Return None if project not found and creation disabled

#### 3.3 Task Retrieval and Filtering
- `_get_open_tasks_for_user(project_id: int) -> List[Dict[str, Any]]`: Get open tasks assigned to configured user
  - Filter by assignee ID from settings (`settings.openproject_assigned_user_id`)
  - Filter by ready state (configurable status ID - `settings.openproject_ready_status_id`)
  - Sort by priority or creation date
  - Uses `get_open_work_packages(project_id, assigned_to_user_id)` from OpenProject API client
  - Additional filtering for ready status can be done client-side or by extending the API call

#### 3.4 Task Processing
- `_process_single_task(repo_dir: Path, task: Dict[str, Any], project_id: int) -> Dict[str, Any]`: Process a single task from OpenProject
  - Handle task without ID gracefully
  - Create branch with naming convention: `ai/op-{task_id}-{sanitized_subject}`
  - Create subtasks for implementation steps
  - Execute subtasks using Ralph loop or direct CLI execution
  - Handle no-changes scenario
  - Create PR in GitHub
  - Update OpenProject task status and add comments
  - Manage task dependencies using OpenProject native features

#### 3.5 Subtask Creation
- `_create_subtasks_for_task(task: Dict[str, Any], repo_dir: Path, project_id: int) -> List[Dict[str, Any]]`: Create subtasks for a parent task
  - Analyze task and generate specific subtask descriptions using CLI
  - Fall back to default subtasks if analysis fails
  - Create subtasks in OpenProject via API using `create_subtask(parent_work_package_id, project_id, subject, description)`
  - Return list of created subtask dictionaries

#### 3.6 Subtask Analysis
- `_analyze_and_generate_subtasks(task_subject: str, task_description: str, repo_dir: Path) -> List[str]`: Generate subtask descriptions using CLI
  - Prompt CLI to analyze task and create breakdown of subtasks
  - Parse numbered or bulleted list output
  - Return list of subtask descriptions

#### 3.7 Ralph Loop Integration
- `_execute_with_ralph_loop(repo_dir: Path, task: Dict[str, Any], subtasks: List[Dict[str, Any]], branch_name: str, project_id: int) -> Dict[str, Any]`: Execute task processing using Ralph loop
  - Create plan file from subtasks
  - Execute each subtask as a step in the Ralph loop
  - Handle step execution, acceptance checks, and updates
  - Commit changes after each successful step
  - Return execution results

### 4. Helper Methods

#### 4.1 Plan Management
- `_create_task_plan(plan_path: Path, task: Dict[str, Any], subtasks: List[Dict[str, Any]], branch_name: str) -> Plan`: Create a plan file for the task based on subtasks
- `_build_step_instructions(...)`: Build instructions for a single step
- `_build_progress_info(plan: Plan) -> str`: Build progress information string

#### 4.2 Instruction Building
- `_build_instructions(task_subject: str, task_description: str, branch_name: Optional[str] = None) -> str`: Build the instructions string from task subject and description
- Include standard development workflow plan:
  1. Understand requirements
  2. Explore codebase
  3. Identify reusable components
  4. Design solution
  5. Write/update tests
  6. Implement solution
  7. Run lint
  8. Run tests
  9. Commit changes
  10. Push changes

#### 4.3 Error Handling
- `_create_error_result(start_time: float, repo_path: Path, error_msg: str) -> Dict[str, Any]`: Create an error result dictionary
- Proper exception handling with logging in all public methods

### 5. Branch Naming Convention

Following the pattern from GithubIssueWorker but adapted for OpenProject:
- Format: `ai/op-{task_id}-{sanitized_subject}`
- Example: `ai/op-42-implement-user-authentication`
- Subject sanitized to lowercase, limited to 30 characters, special characters replaced with hyphens

### 6. Dependency Handling

Using OpenProject native features:
- Before processing a task, check if all dependencies are in closed state
- Only work on tasks where all dependencies are completed
- Optionally create/update dependencies between subtasks using OpenProject API
- Leverage OpenProject's built-in dependency tracking rather than reimplementing
- Dependencies can be checked by retrieving the work package and examining its relationships

### 7. Configuration

All settings must be configurable through `settings.main`:

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

openproject_ready_status_id: int = Field(
    default=1,
    description="Status ID that indicates a task is ready to be worked on"
)

openproject_in_progress_status_id: int = Field(
    default=2,
    description="Status ID to set when task is in progress"
)

openproject_closed_status_id: int = Field(
    default=3,
    description="Status ID that indicates a task is closed/completed"
)

openproject_project_prefix: str = Field(
    default="",
    description="Optional prefix for project identifiers"
)

openproject_create_projects: bool = Field(
    default=True,
    description="Whether to automatically create projects that don't exist"
)

openproject_max_tasks_per_run: int = Field(
    default=1,
    description="Maximum number of tasks to process per repository per run"
)
```

### 8. Data Structures

#### 8.1 Work Package (Task) from OpenProject
```json
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
    },
    "dependencies": [
        {
            "id": int,
            "subject": str,
            "status": {"id": int, "name": str}
        }
    ]
}
```

#### 8.2 Project from OpenProject
```json
{
    "id": int,
    "name": str,
    "identifier": str,
    "_links": {
        "self": {"href": str}
    }
}
```

### 9. Error Handling and Logging

- Log all significant events at appropriate levels (INFO, WARNING, ERROR)
- Handle API failures gracefully: log error, return empty/default values, continue processing
- Handle missing configurations: return error result without processing
- Handle branch creation failures: log error and skip task
- Handle PR creation failures: log error but continue with task updates
- Handle Ralph loop failures: log error and don't mark task as in progress
- Ensure all external API calls are wrapped in try/catch blocks

### 10. Differences from GithubIssueWorker

| Aspect | GithubIssueWorker | OpenProjectWorker |
|--------|-------------------|-------------------|
| Task source | GitHub Issues | OpenProject Work Packages |
| Task filter | By label and creator | By assignee and ready status |
| Branch prefix | `ai/issue-` | `ai/op-` |
| Subtask creation | N/A (uses .ralph markdown) | Creates subtasks in OpenProject |
| Status update | Close issue | Set to in progress status |
| Project matching | Repository-based | Name match with OpenProject project |
| Dependency handling | Not implemented | Uses OpenProject native dependencies |
| Implementation steps storage | Markdown in .ralph directory | Subtasks in OpenProject |

### 11. Testing Strategy

Tests should mirror those in `test_github_issue_worker.py` but adapted for OpenProject:
1. Test initialization with various parameters
2. Test with no tasks available
3. Test dry run mode
4. Test branch name sanitization
5. Test error handling scenarios
6. Test subtask generation
7. Test project creation logic
8. Test dependency checking
9. Mock OpenProject API responses
10. Verify `make test` success requirement is enforced

## Conclusion

This specification provides a complete blueprint for implementing the OpenProjectWorker following the same patterns as the GithubIssueWorker while adapting to OpenProject's API and capabilities. The worker will enable automated task processing from OpenProject repositories with proper branching, execution, PR creation, and status updates.