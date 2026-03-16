"""OpenProject operations utilities for workers.

This module provides pure functions for common OpenProject operations
using the OpenProject REST API v3 via the generated OpenAPI client.
"""

import logging
from typing import Any, Dict, List, Optional

from openproject.openapi_client.openproject_client import (
    ApiClient,
    Configuration,
)
from openproject.openapi_client.openproject_client.api import (
    ActivitiesApi,
    ProjectsApi,
    StatusesApi,
    TypesApi,
    UsersApi,
    WorkPackagesApi,
)
from openproject.openapi_client.openproject_client.exceptions import ApiException
from openproject.openapi_client.openproject_client.models import (
    ActivityCommentWriteModel,
    ProjectModel,
    WorkPackageModel,
    WorkPackagePatchModel,
    WorkPackageWriteModel,
)
from settings.main import settings

logger = logging.getLogger(__name__)


class OpenProjectOperationError(Exception):
    """Exception raised when OpenProject operations fail."""

    pass


def _get_configuration() -> Configuration:
    """Get OpenAPI client configuration.

    OpenProject uses BasicAuth where:
    - Username: 'apikey' (literal string)
    - Password: the API token

    Returns:
        Configured Configuration instance
    """
    configuration = Configuration(
        host=settings.openproject_url.rstrip("/"),
        username="apikey",
        password=settings.openproject_api_token,
    )
    return configuration


def _get_api_client() -> ApiClient:
    """Get an API client configured for OpenProject.

    Returns:
        Configured ApiClient instance
    """
    return ApiClient(configuration=_get_configuration())


def get_projects() -> List[Dict[str, Any]]:
    """Get list of all projects from OpenProject.

    Returns:
        List of dictionaries containing project information.
    """
    try:
        with _get_api_client() as api_client:
            api = ProjectsApi(api_client)
            result = api.list_projects()
            if result and hasattr(result, "_embedded") and result._embedded:
                elements = getattr(result._embedded, "elements", [])
                return [api_client.sanitize_for_serialization(e) for e in elements]
            return []
    except ApiException as e:
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
        with _get_api_client() as api_client:
            api = ProjectsApi(api_client)
            result = api.list_projects()
            if result and hasattr(result, "_embedded") and result._embedded:
                elements = getattr(result._embedded, "elements", [])
                for project in elements:
                    if hasattr(project, "identifier") and project.identifier == identifier:
                        return api_client.sanitize_for_serialization(project)
            return None
    except ApiException as e:
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
        with _get_api_client() as api_client:
            api = ProjectsApi(api_client)
            result = api.list_projects(filters=f'[{{"name":{{"operator":"~","values":["{name}"]}}}}]')
            if result and hasattr(result, "_embedded") and result._embedded:
                elements = getattr(result._embedded, "elements", [])
                for project in elements:
                    if hasattr(project, "name") and project.name == name:
                        return api_client.sanitize_for_serialization(project)
                if elements:
                    return api_client.sanitize_for_serialization(elements[0])
            return None
    except ApiException as e:
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
        with _get_api_client() as api_client:
            api = ProjectsApi(api_client)
            project_data: Dict[str, Any] = {
                "name": name,
                "identifier": identifier,
            }
            if description:
                project_data["description"] = {"format": "markdown", "raw": description}

            project_model = ProjectModel(**project_data)
            result = api.create_project(project_model=project_model)
            logger.info(f"Created OpenProject project: {name} ({identifier})")
            return api_client.sanitize_for_serialization(result)
    except ApiException as e:
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
        with _get_api_client() as api_client:
            api = WorkPackagesApi(api_client)
            filters_list = []
            if assigned_to_user_id:
                filters_list.append(f'{{"assignee":{{"operator":"=","values":["{assigned_to_user_id}"]}}}}')
            if status_id:
                filters_list.append(f'{{"status":{{"operator":"=","values":["{status_id}"]}}}}')

            filters = f"[{','.join(filters_list)}]" if filters_list else "[]"
            result = api.list_work_packages(id=project_id, filters=filters)
            if result and hasattr(result, "_embedded") and result._embedded:
                elements = getattr(result._embedded, "elements", [])
                return [api_client.sanitize_for_serialization(e) for e in elements]
            return []
    except ApiException as e:
        logger.error(f"Failed to get work packages for project {project_id}: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error getting work packages: {e}")
        return []


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
        with _get_api_client() as api_client:
            api = WorkPackagesApi(api_client)
            result = api.view_work_package(id=work_package_id)
            return api_client.sanitize_for_serialization(result)
    except ApiException as e:
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
        with _get_api_client() as api_client:
            api = WorkPackagesApi(api_client)
            wp_data: Dict[str, Any] = {
                "subject": subject,
                "_links": {
                    "project": {"href": f"/api/v3/projects/{project_id}"},
                },
            }

            if description:
                wp_data["description"] = {"raw": description}

            if type_id:
                wp_data["_links"]["type"] = {"href": f"/api/v3/types/{type_id}"}

            if parent_id:
                wp_data["_links"]["parent"] = {"href": f"/api/v3/work_packages/{parent_id}"}

            if assignee_id:
                wp_data["_links"]["assignee"] = {"href": f"/api/v3/users/{assignee_id}"}

            wp_model = WorkPackageWriteModel(**wp_data)
            result = api.create_work_package(id=project_id, work_package_write_model=wp_model)
            logger.info(f"Created work package: {subject}")
            return api_client.sanitize_for_serialization(result)
    except ApiException as e:
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
        with _get_api_client() as api_client:
            api = WorkPackagesApi(api_client)
            patch_data: Dict[str, Any] = {"lockVersion": lock_version}

            links: Dict[str, Any] = {}
            if status_id is not None:
                links["status"] = {"href": f"/api/v3/statuses/{status_id}"}

            if assignee_id is not None:
                links["assignee"] = {"href": f"/api/v3/users/{assignee_id}"}

            if links:
                patch_data["_links"] = links

            if description is not None:
                patch_data["description"] = {"raw": description}

            if subject is not None:
                patch_data["subject"] = subject

            patch_model = WorkPackagePatchModel(**patch_data)
            result = api.update_work_package(id=work_package_id, work_package_patch_model=patch_model)
            logger.info(f"Updated work package {work_package_id}")
            return api_client.sanitize_for_serialization(result)
    except ApiException as e:
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
        with _get_api_client() as api_client:
            api = WorkPackagesApi(api_client)
            comment_model = ActivityCommentWriteModel(comment={"raw": comment})
            api.create_work_package_activity(id=work_package_id, activity_comment_write_model=comment_model)
            logger.info(f"Added comment to work package {work_package_id}")
            return True
    except ApiException as e:
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
        with _get_api_client() as api_client:
            api = StatusesApi(api_client)
            result = api.list_available_statuses_for_project(id=project_id)
            if result and hasattr(result, "_embedded") and result._embedded:
                elements = getattr(result._embedded, "elements", [])
                return [api_client.sanitize_for_serialization(e) for e in elements]
            return []
    except ApiException as e:
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
        with _get_api_client() as api_client:
            api = UsersApi(api_client)
            result = api.view_user(id=user_id)
            return api_client.sanitize_for_serialization(result)
    except ApiException as e:
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
        with _get_api_client() as api_client:
            api = UsersApi(api_client)
            result = api.view_current_user()
            return api_client.sanitize_for_serialization(result)
    except ApiException as e:
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
        with _get_api_client() as api_client:
            api = TypesApi(api_client)
            result = api.list_types_for_project(id=project_id)
            if result and hasattr(result, "_embedded") and result._embedded:
                elements = getattr(result._embedded, "elements", [])
                return [api_client.sanitize_for_serialization(e) for e in elements]
            return []
    except ApiException as e:
        logger.error(f"Failed to get work package types for project {project_id}: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error getting work package types: {e}")
        return []
