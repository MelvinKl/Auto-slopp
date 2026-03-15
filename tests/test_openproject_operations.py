"""Tests for OpenProject operations utilities."""

from unittest.mock import MagicMock, patch

import httpx
import pytest

from auto_slopp.utils.openproject_operations import (
    OpenProjectOperationError,
    _get_client,
    add_comment_to_work_package,
    create_project,
    create_subtask,
    create_work_package,
    get_available_statuses,
    get_current_user,
    get_open_work_packages,
    get_project_by_identifier,
    get_project_by_name,
    get_projects,
    get_user,
    get_work_package,
    get_work_package_types,
    get_work_packages,
    set_work_package_status,
    update_work_package,
)


class TestGetClient:
    """Tests for _get_client function."""

    def test_get_client_configured_correctly(self):
        """Test that client is configured with correct headers."""
        with patch("auto_slopp.utils.openproject_operations.settings") as mock_settings:
            mock_settings.openproject_url = "https://test.openproject.com/"
            mock_settings.openproject_api_token = "test_token"

            client = _get_client()

            assert client is not None
            assert "Bearer test_token" in client.headers.get("Authorization", "")
            assert client.headers.get("Content-Type") == "application/json"
            client.close()


class TestGetProjects:
    """Tests for get_projects function."""

    def test_get_projects_success(self):
        """Test successful retrieval of projects."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "_embedded": {
                "elements": [
                    {"id": 1, "name": "Project 1"},
                    {"id": 2, "name": "Project 2"},
                ]
            }
        }
        mock_response.raise_for_status = MagicMock()

        with (
            patch("auto_slopp.utils.openproject_operations._get_client") as mock_client,
            patch("auto_slopp.utils.openproject_operations.settings"),
        ):
            mock_client.return_value.__enter__ = MagicMock(
                return_value=MagicMock(get=MagicMock(return_value=mock_response))
            )
            mock_client.return_value.__exit__ = MagicMock(return_value=False)

            projects = get_projects()

            assert len(projects) == 2
            assert projects[0]["name"] == "Project 1"

    def test_get_projects_empty(self):
        """Test retrieval when no projects exist."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"_embedded": {"elements": []}}
        mock_response.raise_for_status = MagicMock()

        with (
            patch("auto_slopp.utils.openproject_operations._get_client") as mock_client,
            patch("auto_slopp.utils.openproject_operations.settings"),
        ):
            mock_client.return_value.__enter__ = MagicMock(
                return_value=MagicMock(get=MagicMock(return_value=mock_response))
            )
            mock_client.return_value.__exit__ = MagicMock(return_value=False)

            projects = get_projects()

            assert projects == []

    def test_get_projects_http_error(self):
        """Test handling of HTTP errors."""
        with (
            patch("auto_slopp.utils.openproject_operations._get_client") as mock_client,
            patch("auto_slopp.utils.openproject_operations.settings"),
        ):
            mock_client_instance = MagicMock()
            mock_client_instance.get.side_effect = httpx.HTTPError("Connection failed")
            mock_client.return_value.__enter__ = MagicMock(return_value=mock_client_instance)
            mock_client.return_value.__exit__ = MagicMock(return_value=False)

            projects = get_projects()

            assert projects == []


class TestGetProjectByIdentifier:
    """Tests for get_project_by_identifier function."""

    def test_get_project_by_identifier_found(self):
        """Test finding project by identifier."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"_embedded": {"elements": [{"id": 1, "identifier": "test_project"}]}}
        mock_response.raise_for_status = MagicMock()

        with (
            patch("auto_slopp.utils.openproject_operations._get_client") as mock_client,
            patch("auto_slopp.utils.openproject_operations.settings"),
        ):
            mock_client_instance = MagicMock()
            mock_client_instance.get.return_value = mock_response
            mock_client.return_value.__enter__ = MagicMock(return_value=mock_client_instance)
            mock_client.return_value.__exit__ = MagicMock(return_value=False)

            project = get_project_by_identifier("test_project")

            assert project is not None
            assert project["identifier"] == "test_project"

    def test_get_project_by_identifier_not_found(self):
        """Test when project not found by identifier."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"_embedded": {"elements": []}}
        mock_response.raise_for_status = MagicMock()

        with (
            patch("auto_slopp.utils.openproject_operations._get_client") as mock_client,
            patch("auto_slopp.utils.openproject_operations.settings"),
        ):
            mock_client_instance = MagicMock()
            mock_client_instance.get.return_value = mock_response
            mock_client.return_value.__enter__ = MagicMock(return_value=mock_client_instance)
            mock_client.return_value.__exit__ = MagicMock(return_value=False)

            project = get_project_by_identifier("nonexistent")

            assert project is None


class TestGetProjectByName:
    """Tests for get_project_by_name function."""

    def test_get_project_by_name_found(self):
        """Test finding project by name."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"_embedded": {"elements": [{"id": 1, "name": "Test Project"}]}}
        mock_response.raise_for_status = MagicMock()

        with (
            patch("auto_slopp.utils.openproject_operations._get_client") as mock_client,
            patch("auto_slopp.utils.openproject_operations.settings"),
        ):
            mock_client_instance = MagicMock()
            mock_client_instance.get.return_value = mock_response
            mock_client.return_value.__enter__ = MagicMock(return_value=mock_client_instance)
            mock_client.return_value.__exit__ = MagicMock(return_value=False)

            project = get_project_by_name("Test Project")

            assert project is not None
            assert project["name"] == "Test Project"

    def test_get_project_by_name_not_found(self):
        """Test when project not found by name."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"_embedded": {"elements": []}}
        mock_response.raise_for_status = MagicMock()

        with (
            patch("auto_slopp.utils.openproject_operations._get_client") as mock_client,
            patch("auto_slopp.utils.openproject_operations.settings"),
        ):
            mock_client_instance = MagicMock()
            mock_client_instance.get.return_value = mock_response
            mock_client.return_value.__enter__ = MagicMock(return_value=mock_client_instance)
            mock_client.return_value.__exit__ = MagicMock(return_value=False)

            project = get_project_by_name("Nonexistent Project")

            assert project is None


class TestCreateProject:
    """Tests for create_project function."""

    def test_create_project_success(self):
        """Test successful project creation."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "id": 1,
            "name": "New Project",
            "identifier": "new_project",
        }
        mock_response.raise_for_status = MagicMock()

        with (
            patch("auto_slopp.utils.openproject_operations._get_client") as mock_client,
            patch("auto_slopp.utils.openproject_operations.settings"),
        ):
            mock_client_instance = MagicMock()
            mock_client_instance.post.return_value = mock_response
            mock_client.return_value.__enter__ = MagicMock(return_value=mock_client_instance)
            mock_client.return_value.__exit__ = MagicMock(return_value=False)

            project = create_project(
                name="New Project",
                identifier="new_project",
                description="Project description",
            )

            assert project is not None
            assert project["name"] == "New Project"
            mock_client_instance.post.assert_called_once()

    def test_create_project_without_description(self):
        """Test project creation without description."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "id": 1,
            "name": "New Project",
            "identifier": "new_project",
        }
        mock_response.raise_for_status = MagicMock()

        with (
            patch("auto_slopp.utils.openproject_operations._get_client") as mock_client,
            patch("auto_slopp.utils.openproject_operations.settings"),
        ):
            mock_client_instance = MagicMock()
            mock_client_instance.post.return_value = mock_response
            mock_client.return_value.__enter__ = MagicMock(return_value=mock_client_instance)
            mock_client.return_value.__exit__ = MagicMock(return_value=False)

            project = create_project(name="New Project", identifier="new_project")

            assert project is not None

    def test_create_project_http_error(self):
        """Test handling HTTP error during project creation."""
        with (
            patch("auto_slopp.utils.openproject_operations._get_client") as mock_client,
            patch("auto_slopp.utils.openproject_operations.settings"),
        ):
            mock_client_instance = MagicMock()
            mock_client_instance.post.side_effect = httpx.HTTPError("Creation failed")
            mock_client.return_value.__enter__ = MagicMock(return_value=mock_client_instance)
            mock_client.return_value.__exit__ = MagicMock(return_value=False)

            project = create_project(name="New Project", identifier="new_project")

            assert project is None


class TestGetWorkPackages:
    """Tests for get_work_packages function."""

    def test_get_work_packages_success(self):
        """Test successful retrieval of work packages."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "_embedded": {
                "elements": [
                    {"id": 1, "subject": "Task 1"},
                    {"id": 2, "subject": "Task 2"},
                ]
            }
        }
        mock_response.raise_for_status = MagicMock()

        with (
            patch("auto_slopp.utils.openproject_operations._get_client") as mock_client,
            patch("auto_slopp.utils.openproject_operations.settings"),
        ):
            mock_client_instance = MagicMock()
            mock_client_instance.get.return_value = mock_response
            mock_client.return_value.__enter__ = MagicMock(return_value=mock_client_instance)
            mock_client.return_value.__exit__ = MagicMock(return_value=False)

            work_packages = get_work_packages(project_id=1)

            assert len(work_packages) == 2
            assert work_packages[0]["subject"] == "Task 1"

    def test_get_work_packages_with_filters(self):
        """Test retrieval of work packages with filters."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"_embedded": {"elements": [{"id": 1, "subject": "Filtered Task"}]}}
        mock_response.raise_for_status = MagicMock()

        with (
            patch("auto_slopp.utils.openproject_operations._get_client") as mock_client,
            patch("auto_slopp.utils.openproject_operations.settings"),
        ):
            mock_client_instance = MagicMock()
            mock_client_instance.get.return_value = mock_response
            mock_client.return_value.__enter__ = MagicMock(return_value=mock_client_instance)
            mock_client.return_value.__exit__ = MagicMock(return_value=False)

            work_packages = get_work_packages(
                project_id=1,
                assigned_to_user_id=5,
                status_id=7,
            )

            assert len(work_packages) == 1
            call_args = mock_client_instance.get.call_args
            assert "filters" in call_args.kwargs.get("params", {})

    def test_get_work_packages_filter_format_is_json(self):
        """Test that filters are formatted as proper JSON with double quotes."""
        import json

        mock_response = MagicMock()
        mock_response.json.return_value = {"_embedded": {"elements": []}}
        mock_response.raise_for_status = MagicMock()

        with (
            patch("auto_slopp.utils.openproject_operations._get_client") as mock_client,
            patch("auto_slopp.utils.openproject_operations.settings"),
        ):
            mock_client_instance = MagicMock()
            mock_client_instance.get.return_value = mock_response
            mock_client.return_value.__enter__ = MagicMock(return_value=mock_client_instance)
            mock_client.return_value.__exit__ = MagicMock(return_value=False)

            get_work_packages(project_id=1, assigned_to_user_id=5)

            call_args = mock_client_instance.get.call_args
            filters_str = call_args.kwargs.get("params", {}).get("filters", "")
            filters = json.loads(filters_str)
            expected_filter = [{"assigned_to": {"operator": "=", "values": ["5"]}}]
            assert filters == expected_filter
            assert '"' in filters_str
            assert "'" not in filters_str


class TestGetOpenWorkPackages:
    """Tests for get_open_work_packages function."""

    def test_get_open_work_packages_calls_get_work_packages(self):
        """Test that get_open_work_packages calls get_work_packages correctly."""
        with patch("auto_slopp.utils.openproject_operations.get_work_packages") as mock_get_wp:
            mock_get_wp.return_value = [{"id": 1, "subject": "Open Task"}]

            result = get_open_work_packages(project_id=1, assigned_to_user_id=5)

            assert len(result) == 1
            mock_get_wp.assert_called_once_with(
                project_id=1,
                assigned_to_user_id=5,
                status_id=None,
            )


class TestGetWorkPackage:
    """Tests for get_work_package function."""

    def test_get_work_package_found(self):
        """Test finding a work package by ID."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": 1, "subject": "Test Task"}
        mock_response.raise_for_status = MagicMock()

        with (
            patch("auto_slopp.utils.openproject_operations._get_client") as mock_client,
            patch("auto_slopp.utils.openproject_operations.settings"),
        ):
            mock_client_instance = MagicMock()
            mock_client_instance.get.return_value = mock_response
            mock_client.return_value.__enter__ = MagicMock(return_value=mock_client_instance)
            mock_client.return_value.__exit__ = MagicMock(return_value=False)

            wp = get_work_package(1)

            assert wp is not None
            assert wp["id"] == 1

    def test_get_work_package_not_found(self):
        """Test when work package not found."""
        with (
            patch("auto_slopp.utils.openproject_operations._get_client") as mock_client,
            patch("auto_slopp.utils.openproject_operations.settings"),
        ):
            mock_client_instance = MagicMock()
            mock_client_instance.get.side_effect = httpx.HTTPError("Not found")
            mock_client.return_value.__enter__ = MagicMock(return_value=mock_client_instance)
            mock_client.return_value.__exit__ = MagicMock(return_value=False)

            wp = get_work_package(999)

            assert wp is None


class TestCreateWorkPackage:
    """Tests for create_work_package function."""

    def test_create_work_package_success(self):
        """Test successful work package creation."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": 1, "subject": "New Task"}
        mock_response.raise_for_status = MagicMock()

        with (
            patch("auto_slopp.utils.openproject_operations._get_client") as mock_client,
            patch("auto_slopp.utils.openproject_operations.settings"),
        ):
            mock_client_instance = MagicMock()
            mock_client_instance.post.return_value = mock_response
            mock_client.return_value.__enter__ = MagicMock(return_value=mock_client_instance)
            mock_client.return_value.__exit__ = MagicMock(return_value=False)

            wp = create_work_package(
                project_id=1,
                subject="New Task",
                description="Task description",
            )

            assert wp is not None
            assert wp["subject"] == "New Task"

    def test_create_work_package_with_all_options(self):
        """Test work package creation with all options."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": 1, "subject": "New Task"}
        mock_response.raise_for_status = MagicMock()

        with (
            patch("auto_slopp.utils.openproject_operations._get_client") as mock_client,
            patch("auto_slopp.utils.openproject_operations.settings"),
        ):
            mock_client_instance = MagicMock()
            mock_client_instance.post.return_value = mock_response
            mock_client.return_value.__enter__ = MagicMock(return_value=mock_client_instance)
            mock_client.return_value.__exit__ = MagicMock(return_value=False)

            wp = create_work_package(
                project_id=1,
                subject="New Task",
                description="Task description",
                type_id=1,
                parent_id=10,
                assignee_id=5,
            )

            assert wp is not None
            call_args = mock_client_instance.post.call_args
            payload = call_args.kwargs.get("json", {})
            assert "_links" in payload
            assert "parent" in payload["_links"]
            assert "assignee" in payload["_links"]


class TestCreateSubtask:
    """Tests for create_subtask function."""

    def test_create_subtask_calls_create_work_package(self):
        """Test that create_subtask calls create_work_package correctly."""
        with patch("auto_slopp.utils.openproject_operations.create_work_package") as mock_create_wp:
            mock_create_wp.return_value = {"id": 1, "subject": "Subtask"}

            result = create_subtask(
                parent_work_package_id=10,
                project_id=1,
                subject="Subtask",
                description="Subtask description",
            )

            assert result is not None
            mock_create_wp.assert_called_once_with(
                project_id=1,
                subject="Subtask",
                description="Subtask description",
                parent_id=10,
            )


class TestUpdateWorkPackage:
    """Tests for update_work_package function."""

    def test_update_work_package_status(self):
        """Test updating work package status."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": 1, "subject": "Updated Task"}
        mock_response.raise_for_status = MagicMock()

        with (
            patch("auto_slopp.utils.openproject_operations._get_client") as mock_client,
            patch("auto_slopp.utils.openproject_operations.settings"),
        ):
            mock_client_instance = MagicMock()
            mock_client_instance.patch.return_value = mock_response
            mock_client.return_value.__enter__ = MagicMock(return_value=mock_client_instance)
            mock_client.return_value.__exit__ = MagicMock(return_value=False)

            wp = update_work_package(
                work_package_id=1,
                lock_version=1,
                status_id=7,
            )

            assert wp is not None
            call_args = mock_client_instance.patch.call_args
            payload = call_args.kwargs.get("json", {})
            assert payload["lockVersion"] == 1

    def test_update_work_package_all_fields(self):
        """Test updating all work package fields."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": 1, "subject": "Updated Task"}
        mock_response.raise_for_status = MagicMock()

        with (
            patch("auto_slopp.utils.openproject_operations._get_client") as mock_client,
            patch("auto_slopp.utils.openproject_operations.settings"),
        ):
            mock_client_instance = MagicMock()
            mock_client_instance.patch.return_value = mock_response
            mock_client.return_value.__enter__ = MagicMock(return_value=mock_client_instance)
            mock_client.return_value.__exit__ = MagicMock(return_value=False)

            wp = update_work_package(
                work_package_id=1,
                lock_version=1,
                status_id=7,
                assignee_id=5,
                description="New description",
                subject="New subject",
            )

            assert wp is not None


class TestSetWorkPackageStatus:
    """Tests for set_work_package_status function."""

    def test_set_work_package_status_calls_update(self):
        """Test that set_work_package_status calls update_work_package."""
        with patch("auto_slopp.utils.openproject_operations.update_work_package") as mock_update:
            mock_update.return_value = {"id": 1, "subject": "Task"}

            result = set_work_package_status(
                work_package_id=1,
                lock_version=1,
                status_id=7,
            )

            assert result is not None
            mock_update.assert_called_once_with(
                work_package_id=1,
                lock_version=1,
                status_id=7,
            )


class TestAddCommentToWorkPackage:
    """Tests for add_comment_to_work_package function."""

    def test_add_comment_success(self):
        """Test successfully adding a comment."""
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()

        with (
            patch("auto_slopp.utils.openproject_operations._get_client") as mock_client,
            patch("auto_slopp.utils.openproject_operations.settings"),
        ):
            mock_client_instance = MagicMock()
            mock_client_instance.post.return_value = mock_response
            mock_client.return_value.__enter__ = MagicMock(return_value=mock_client_instance)
            mock_client.return_value.__exit__ = MagicMock(return_value=False)

            result = add_comment_to_work_package(
                work_package_id=1,
                comment="This is a comment",
            )

            assert result is True

    def test_add_comment_failure(self):
        """Test handling failure when adding comment."""
        with (
            patch("auto_slopp.utils.openproject_operations._get_client") as mock_client,
            patch("auto_slopp.utils.openproject_operations.settings"),
        ):
            mock_client_instance = MagicMock()
            mock_client_instance.post.side_effect = httpx.HTTPError("Failed")
            mock_client.return_value.__enter__ = MagicMock(return_value=mock_client_instance)
            mock_client.return_value.__exit__ = MagicMock(return_value=False)

            result = add_comment_to_work_package(
                work_package_id=1,
                comment="This is a comment",
            )

            assert result is False


class TestGetAvailableStatuses:
    """Tests for get_available_statuses function."""

    def test_get_available_statuses_success(self):
        """Test successful retrieval of statuses."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "_embedded": {
                "elements": [
                    {"id": 1, "name": "New"},
                    {"id": 7, "name": "In Progress"},
                ]
            }
        }
        mock_response.raise_for_status = MagicMock()

        with (
            patch("auto_slopp.utils.openproject_operations._get_client") as mock_client,
            patch("auto_slopp.utils.openproject_operations.settings"),
        ):
            mock_client_instance = MagicMock()
            mock_client_instance.get.return_value = mock_response
            mock_client.return_value.__enter__ = MagicMock(return_value=mock_client_instance)
            mock_client.return_value.__exit__ = MagicMock(return_value=False)

            statuses = get_available_statuses(project_id=1)

            assert len(statuses) == 2
            assert statuses[0]["name"] == "New"

    def test_get_available_statuses_error(self):
        """Test handling error when getting statuses."""
        with (
            patch("auto_slopp.utils.openproject_operations._get_client") as mock_client,
            patch("auto_slopp.utils.openproject_operations.settings"),
        ):
            mock_client_instance = MagicMock()
            mock_client_instance.get.side_effect = httpx.HTTPError("Failed")
            mock_client.return_value.__enter__ = MagicMock(return_value=mock_client_instance)
            mock_client.return_value.__exit__ = MagicMock(return_value=False)

            statuses = get_available_statuses(project_id=1)

            assert statuses == []


class TestGetUser:
    """Tests for get_user function."""

    def test_get_user_found(self):
        """Test finding a user by ID."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": 1, "name": "Test User"}
        mock_response.raise_for_status = MagicMock()

        with (
            patch("auto_slopp.utils.openproject_operations._get_client") as mock_client,
            patch("auto_slopp.utils.openproject_operations.settings"),
        ):
            mock_client_instance = MagicMock()
            mock_client_instance.get.return_value = mock_response
            mock_client.return_value.__enter__ = MagicMock(return_value=mock_client_instance)
            mock_client.return_value.__exit__ = MagicMock(return_value=False)

            user = get_user(1)

            assert user is not None
            assert user["name"] == "Test User"

    def test_get_user_not_found(self):
        """Test when user not found."""
        with (
            patch("auto_slopp.utils.openproject_operations._get_client") as mock_client,
            patch("auto_slopp.utils.openproject_operations.settings"),
        ):
            mock_client_instance = MagicMock()
            mock_client_instance.get.side_effect = httpx.HTTPError("Not found")
            mock_client.return_value.__enter__ = MagicMock(return_value=mock_client_instance)
            mock_client.return_value.__exit__ = MagicMock(return_value=False)

            user = get_user(999)

            assert user is None


class TestGetCurrentUser:
    """Tests for get_current_user function."""

    def test_get_current_user_success(self):
        """Test getting current user."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": 1, "name": "Current User"}
        mock_response.raise_for_status = MagicMock()

        with (
            patch("auto_slopp.utils.openproject_operations._get_client") as mock_client,
            patch("auto_slopp.utils.openproject_operations.settings"),
        ):
            mock_client_instance = MagicMock()
            mock_client_instance.get.return_value = mock_response
            mock_client.return_value.__enter__ = MagicMock(return_value=mock_client_instance)
            mock_client.return_value.__exit__ = MagicMock(return_value=False)

            user = get_current_user()

            assert user is not None
            assert user["name"] == "Current User"

    def test_get_current_user_error(self):
        """Test handling error when getting current user."""
        with (
            patch("auto_slopp.utils.openproject_operations._get_client") as mock_client,
            patch("auto_slopp.utils.openproject_operations.settings"),
        ):
            mock_client_instance = MagicMock()
            mock_client_instance.get.side_effect = httpx.HTTPError("Failed")
            mock_client.return_value.__enter__ = MagicMock(return_value=mock_client_instance)
            mock_client.return_value.__exit__ = MagicMock(return_value=False)

            user = get_current_user()

            assert user is None


class TestGetWorkPackageTypes:
    """Tests for get_work_package_types function."""

    def test_get_work_package_types_success(self):
        """Test successful retrieval of work package types."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "_embedded": {
                "elements": [
                    {"id": 1, "name": "Task"},
                    {"id": 2, "name": "Feature"},
                ]
            }
        }
        mock_response.raise_for_status = MagicMock()

        with (
            patch("auto_slopp.utils.openproject_operations._get_client") as mock_client,
            patch("auto_slopp.utils.openproject_operations.settings"),
        ):
            mock_client_instance = MagicMock()
            mock_client_instance.get.return_value = mock_response
            mock_client.return_value.__enter__ = MagicMock(return_value=mock_client_instance)
            mock_client.return_value.__exit__ = MagicMock(return_value=False)

            types = get_work_package_types(project_id=1)

            assert len(types) == 2
            assert types[0]["name"] == "Task"

    def test_get_work_package_types_error(self):
        """Test handling error when getting work package types."""
        with (
            patch("auto_slopp.utils.openproject_operations._get_client") as mock_client,
            patch("auto_slopp.utils.openproject_operations.settings"),
        ):
            mock_client_instance = MagicMock()
            mock_client_instance.get.side_effect = httpx.HTTPError("Failed")
            mock_client.return_value.__enter__ = MagicMock(return_value=mock_client_instance)
            mock_client.return_value.__exit__ = MagicMock(return_value=False)

            types = get_work_package_types(project_id=1)

            assert types == []


class TestOpenProjectOperationError:
    """Tests for OpenProjectOperationError exception."""

    def test_error_message(self):
        """Test that error message is preserved."""
        error = OpenProjectOperationError("Test error message")
        assert str(error) == "Test error message"
