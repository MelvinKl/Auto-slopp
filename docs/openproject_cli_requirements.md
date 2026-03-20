# OpenProject CLI Requirements

## Overview
This document outlines the requirements for a standalone CLI program used to interact with the OpenProject API. This program will be written in Go and will be utilized by the `OpenProjectWorker` to fetch and manage tasks, subtasks, projects, and dependencies.

## Technical Requirements
- **Language:** Go (Golang)
- **Output Format:** All command outputs must be in valid JSON format to allow easy parsing by the invoking Python scripts.
- **Configuration:** Must support authentication and configuration via environment variables or command-line flags (e.g., `OPENPROJECT_URL`, `OPENPROJECT_API_TOKEN`).

## Core Capabilities

### 1. Project Management
- **Find Project:** Retrieve a project by its name or identifier.
- **Create Project:** Create a new project with a given name and identifier.

### 2. Task (Work Package) Management
- **List Tasks:** Fetch tasks assigned to a specific user ID.
  - Must support filtering by status (e.g., "ready" state).
  - Must be able to sort by priority or creation date.
- **Update Task:** Update the status of a specific task (e.g., transition to "in progress" or "closed").
- **Comment on Task:** Add comments/updates to a specific task.

### 3. Subtask Management
- **Create Subtask:** Create a new subtask (implementation step) linked to a specific parent work package.

### 4. Subtask Generation
- **Analyze Task:** Analyze a parent task's subject and description to generate a structured breakdown of implementation subtasks.
- **Output Format:** Return subtask descriptions as a numbered or bulleted list in JSON format for easy parsing.

### 5. Dependency Management
- **Check Dependencies:** Retrieve relations/dependencies for a specific task.
- **Verify State:** Be able to check if all dependent tasks (blocking the current task) are in a closed state.
- **Create Dependency:** Create a new dependency/relation between two tasks (e.g., "blocks" or "precedes").

## Error Handling
- The CLI must exit with a non-zero status code on failure.
- Errors should be output to `stderr` with clear, descriptive messages, while valid JSON responses should be output to `stdout`.
