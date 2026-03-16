"""OpenProject operations utilities for workers.

This module provides pure functions for common OpenProject operations
using the OpenProject REST API v3 (HAL+JSON format) based on docs/openproject.json.
"""

import base64
import json
import logging
from typing import Any, Dict, List, Optional

import httpx

from settings.main import settings

logger = logging.getLogger(__name__)

_PRIMARY_WORK_PACKAGE_FILTER_NAMES = {
    "assignee": "assignee",
    "status": "status",
}
_LEGACY_WORK_PACKAGE_FILTER_NAMES = {
    "assignee": "assigned_to",
    "status": "status_id",
}


class OpenProjectOperationError(Exception):
    """Exception raised when OpenProject operations fail."""

    pass


def _get_client() -> httpx.Client:
    """Get an HTTP client configured for OpenProject API.

    OpenProject uses BasicAuth where:
    - Username: 'apikey' (literal string)
    - Password: the API token

    Returns:
        Configured httpx.Client instance
    """
    credentials = base64.b64encode(f"apikey:{settings.openproject_api_token}".encode()).decode()
    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/json",
    }
    return httpx.Client(
        base_url=settings.openproject_url.rstrip("/"),
        headers=headers,
        timeout=30.0,
    )


def get_projects() -> List[Dict[str, Any]]:
    """Get list of all projects from OpenProject.

    Returns:
        List of dictionaries containing project information.
    """
    try:
        with _get_client() as client:
            response = client.get("/api/v3/projects")
            response.raise_for_status()
            data = response.json()
            return data.get("_embedded", {}).get("elements", [])
    except httpx.HTTPError as e:
        logger.error(f"Failed to get projects from OpenProject: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error getting projects: {e}")
        return []


def get_project_by_identifier(identifier: str) -> Optional[Dict[str, Any]]:
    """Get a project by its identifier.

    Args:
        identifier: Project identifier (usually matches repo name)

    Returns:
        Project dictionary or None if not found.
    """
    try:
        with _get_client() as client:
            filters = json.dumps(
                [{"name_and_identifier": {"operator": "~", "values": [identifier]}}],
                separators=(",", ":"),
            )
            response = client.get("/api/v3/projects", params={"filters": filters})
            response.raise_for_status()
            data = response.json()
            elements = data.get("_embedded", {}).get("elements", [])
            for project in elements:
                if project.get("identifier") == identifier:
                    return project
            return elements[0] if elements else None
    except httpx.HTTPError as e:
        logger.error(f"Failed to get project {identifier}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error getting project {identifier}: {e}")
        return None


def get_project_by_name(name: str) -> Optional[Dict[str, Any]]:
    """Get a project by its name.

    Args:
        name: Project name

    Returns:
        Project dictionary or None if not found.
    """
    try:
        with _get_client() as client:
            filters = json.dumps(
                [{"name_and_identifier": {"operator": "~", "values": [name]}}],
                separators=(",", ":"),
            )
            response = client.get("/api/v3/projects", params={"filters": filters})
            response.raise_for_status()
            data = response.json()
            elements = data.get("_embedded", {}).get("elements", [])
            for project in elements:
                if project.get("name") == name:
                    return project
            return elements[0] if elements else None
    except httpx.HTTPError as e:
        logger.error(f"Failed to get project by name {name}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error getting project by name {name}: {e}")
        return None


def create_project(
    name: str,
    identifier: str,
    description: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Create a new project in OpenProject.

    Args:
        name: Project name
        identifier: Project identifier (used in URLs)
        description: Optional project description

    Returns:
        Created project dictionary or None if failed.
    """
    try:
        with _get_client() as client:
            payload: Dict[str, Any] = {
                "name": name,
                "identifier": identifier,
            }
            if description:
                payload["description"] = {"raw": description}

            response = client.post("/api/v3/projects", json=payload)
            response.raise_for_status()
            project = response.json()
            logger.info(f"Created OpenProject project: {name} ({identifier})")
            return project
    except httpx.HTTPError as e:
        logger.error(f"Failed to create project {name}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error creating project {name}: {e}")
        return None


def get_work_packages(
    project_id: int,
    assigned_to_user_id: Optional[int] = None,
    status_id: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Get work packages (tasks) for a project.

    Args:
        project_id: OpenProject project ID
        assigned_to_user_id: Filter by assigned user ID
        status_id: Filter by status ID

    Returns:
        List of work package dictionaries.
    """
    try:
        with _get_client() as client:
            params = {
                "filters": _build_work_package_filters(
                    assigned_to_user_id=assigned_to_user_id,
                    status_id=status_id,
                    filter_names=_PRIMARY_WORK_PACKAGE_FILTER_NAMES,
                )
            }
            response = client.get(f"/api/v3/projects/{project_id}/work_packages", params=params)
            response.raise_for_status()
    except httpx.HTTPStatusError as e:
        if e.response is not None and e.response.status_code == 400:
            try:
                with _get_client() as client:
                    fallback_params = {
                        "filters": _build_work_package_filters(
                            assigned_to_user_id=assigned_to_user_id,
                            status_id=status_id,
                            filter_names=_LEGACY_WORK_PACKAGE_FILTER_NAMES,
                        )
                    }
                    logger.warning(
                        "Retrying work package request for project %s with legacy filter names",
                        project_id,
                    )
                    response = client.get(
                        f"/api/v3/projects/{project_id}/work_packages",
                        params=fallback_params,
                    )
                    response.raise_for_status()
            except httpx.HTTPError as retry_error:
                logger.error(f"Failed to get work packages for project {project_id}: {retry_error}")
                return []

            data = response.json()
            return data.get("_embedded", {}).get("elements", [])
        logger.error(f"Failed to get work packages for project {project_id}: {e}")
        return []
    except httpx.HTTPError as e:
        logger.error(f"Failed to get work packages for project {project_id}: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error getting work packages: {e}")
        return []

    data = response.json()
    return data.get("_embedded", {}).get("elements", [])


def _build_work_package_filters(
    assigned_to_user_id: Optional[int],
    status_id: Optional[int],
    filter_names: Dict[str, str],
) -> str:
    """Build JSON query filters for work package list requests."""
    filters_list = []
    if assigned_to_user_id is not None:
        filters_list.append(
            {
                filter_names["assignee"]: {
                    "operator": "=",
                    "values": [str(assigned_to_user_id)],
                }
            }
        )
    if status_id is not None:
        filters_list.append(
            {
                filter_names["status"]: {
                    "operator": "=",
                    "values": [str(status_id)],
                }
            }
        )

    return json.dumps(filters_list, separators=(",", ":")) if filters_list else "[]"


def get_open_work_packages(
    project_id: int,
    assigned_to_user_id: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Get open work packages (tasks) for a project.

    Open tasks are those not in a "closed" state.

    Args:
        project_id: OpenProject project ID
        assigned_to_user_id: Filter by assigned user ID

    Returns:
        List of open work package dictionaries.
    """
    return get_work_packages(
        project_id=project_id,
        assigned_to_user_id=assigned_to_user_id,
        status_id=None,
    )


def get_work_package(work_package_id: int) -> Optional[Dict[str, Any]]:
    """Get a single work package by ID.

    Args:
        work_package_id: Work package ID

    Returns:
        Work package dictionary or None if not found.
    """
    try:
        with _get_client() as client:
            response = client.get(f"/api/v3/work_packages/{work_package_id}")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Failed to get work package {work_package_id}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error getting work package {work_package_id}: {e}")
        return None


def create_work_package(
    project_id: int,
    subject: str,
    description: Optional[str] = None,
    type_id: Optional[int] = None,
    parent_id: Optional[int] = None,
    assignee_id: Optional[int] = None,
) -> Optional[Dict[str, Any]]:
    """Create a new work package (task) in a project.

    Args:
        project_id: OpenProject project ID
        subject: Work package subject/title
        description: Optional description (raw markdown)
        type_id: Work package type ID (e.g., Task, Feature, Bug)
        parent_id: Parent work package ID for subtasks
        assignee_id: User ID to assign the task to

    Returns:
        Created work package dictionary or None if failed.
    """
    try:
        with _get_client() as client:
            payload: Dict[str, Any] = {
                "subject": subject,
                "_links": {
                    "project": {"href": f"/api/v3/projects/{project_id}"},
                },
            }

            if description:
                payload["description"] = {"raw": description}

            if type_id:
                payload["_links"]["type"] = {"href": f"/api/v3/types/{type_id}"}

            if parent_id:
                payload["_links"]["parent"] = {"href": f"/api/v3/work_packages/{parent_id}"}

            if assignee_id:
                payload["_links"]["assignee"] = {"href": f"/api/v3/users/{assignee_id}"}

            response = client.post(
                f"/api/v3/projects/{project_id}/work_packages",
                json=payload,
            )
            response.raise_for_status()
            wp = response.json()
            logger.info(f"Created work package: {subject}")
            return wp
    except httpx.HTTPError as e:
        logger.error(f"Failed to create work package {subject}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error creating work package {subject}: {e}")
        return None


def create_subtask(
    parent_work_package_id: int,
    project_id: int,
    subject: str,
    description: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Create a subtask under a parent work package.

    Args:
        parent_work_package_id: Parent work package ID
        project_id: OpenProject project ID
        subject: Subtask subject/title
        description: Optional description

    Returns:
        Created work package dictionary or None if failed.
    """
    return create_work_package(
        project_id=project_id,
        subject=subject,
        description=description,
        parent_id=parent_work_package_id,
    )


def update_work_package(
    work_package_id: int,
    lock_version: int,
    status_id: Optional[int] = None,
    assignee_id: Optional[int] = None,
    description: Optional[str] = None,
    subject: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Update a work package.

    Args:
        work_package_id: Work package ID to update
        lock_version: Current lock version (required for optimistic locking)
        status_id: New status ID
        assignee_id: New assignee user ID
        description: New description
        subject: New subject

    Returns:
        Updated work package dictionary or None if failed.
    """
    try:
        with _get_client() as client:
            payload: Dict[str, Any] = {"lockVersion": lock_version}

            if status_id is not None:
                payload["_links"] = payload.get("_links", {})
                payload["_links"]["status"] = {"href": f"/api/v3/statuses/{status_id}"}

            if assignee_id is not None:
                payload["_links"] = payload.get("_links", {})
                payload["_links"]["assignee"] = {"href": f"/api/v3/users/{assignee_id}"}

            if description is not None:
                payload["description"] = {"raw": description}

            if subject is not None:
                payload["subject"] = subject

            response = client.patch(
                f"/api/v3/work_packages/{work_package_id}",
                json=payload,
            )
            response.raise_for_status()
            wp = response.json()
            logger.info(f"Updated work package {work_package_id}")
            return wp
    except httpx.HTTPError as e:
        logger.error(f"Failed to update work package {work_package_id}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error updating work package {work_package_id}: {e}")
        return None


def set_work_package_status(
    work_package_id: int,
    lock_version: int,
    status_id: int,
) -> Optional[Dict[str, Any]]:
    """Set the status of a work package.

    Args:
        work_package_id: Work package ID
        lock_version: Current lock version
        status_id: New status ID

    Returns:
        Updated work package dictionary or None if failed.
    """
    return update_work_package(
        work_package_id=work_package_id,
        lock_version=lock_version,
        status_id=status_id,
    )


def add_comment_to_work_package(
    work_package_id: int,
    comment: str,
) -> bool:
    """Add a comment to a work package.

    Args:
        work_package_id: Work package ID
        comment: Comment text (markdown supported)

    Returns:
        True if successful, False otherwise.
    """
    try:
        with _get_client() as client:
            payload = {"comment": {"raw": comment}}
            response = client.post(
                f"/api/v3/work_packages/{work_package_id}/activities",
                json=payload,
            )
            response.raise_for_status()
            logger.info(f"Added comment to work package {work_package_id}")
            return True
    except httpx.HTTPError as e:
        logger.error(f"Failed to add comment to work package {work_package_id}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error adding comment to work package {work_package_id}: {e}")
        return False


def get_available_statuses(project_id: int) -> List[Dict[str, Any]]:
    """Get available statuses for a project.

    Args:
        project_id: OpenProject project ID

    Returns:
        List of status dictionaries.
    """
    try:
        with _get_client() as client:
            response = client.get(f"/api/v3/projects/{project_id}/available_statuses")
            response.raise_for_status()
            data = response.json()
            return data.get("_embedded", {}).get("elements", [])
    except httpx.HTTPError as e:
        logger.error(f"Failed to get statuses for project {project_id}: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error getting statuses: {e}")
        return []


def get_user(user_id: int) -> Optional[Dict[str, Any]]:
    """Get user information by ID.

    Args:
        user_id: OpenProject user ID

    Returns:
        User dictionary or None if not found.
    """
    try:
        with _get_client() as client:
            response = client.get(f"/api/v3/users/{user_id}")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Failed to get user {user_id}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error getting user {user_id}: {e}")
        return None


def get_current_user() -> Optional[Dict[str, Any]]:
    """Get the current authenticated user.

    Returns:
        User dictionary or None if not found.
    """
    try:
        with _get_client() as client:
            response = client.get("/api/v3/users/me")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Failed to get current user: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error getting current user: {e}")
        return None


def get_work_package_types(project_id: int) -> List[Dict[str, Any]]:
    """Get available work package types for a project.

    Args:
        project_id: OpenProject project ID

    Returns:
        List of type dictionaries.
    """
    try:
        with _get_client() as client:
            response = client.get(f"/api/v3/projects/{project_id}/types")
            response.raise_for_status()
            data = response.json()
            return data.get("_embedded", {}).get("elements", [])
    except httpx.HTTPError as e:
        logger.error(f"Failed to get work package types for project {project_id}: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error getting work package types: {e}")
        return []
