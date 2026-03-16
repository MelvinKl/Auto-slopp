"""Tests for OpenProject operations utilities."""

from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

from auto_slopp.utils.openproject_operations import (
    OpenProjectOperationError,
    _get_api_client,
    _get_configuration,
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
from openproject.openapi_client.openproject_client.models import ProjectModel


class MockElement:
    """Simple mock element with real attributes."""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class TestGetConfiguration:
    """Tests for _get_configuration function."""

    def test_get_configuration_configured_correctly(self):
        """Test that configuration is set with correct credentials."""
        with patch("auto_slopp.utils.openproject_operations.settings") as mock_settings:
            mock_settings.openproject_url = "https://test.openproject.com/"
            mock_settings.openproject_api_token = "test_token"

            config = _get_configuration()

            assert config is not None
            assert config.host == "https://test.openproject.com"
            assert config.username == "apikey"
            assert config.password == "test_token"


class TestGetApiClient:
    """Tests for _get_api_client function."""

    def test_get_api_client_returns_client(self):
        """Test that API client is returned."""
        with patch("auto_slopp.utils.openproject_operations.settings") as mock_settings:
            mock_settings.openproject_url = "https://test.openproject.com/"
            mock_settings.openproject_api_token = "test_token"

            client = _get_api_client()
            assert client is not None


class TestGetProjects:
    """Tests for get_projects function."""

    def test_get_projects_success(self):
        """Test successful retrieval of projects."""
        mock_result = MagicMock()
        mock_result._embedded = MagicMock()
        mock_result._embedded.elements = [
            MockElement(identifier="project1", name="Project 1"),
            MockElement(identifier="project2", name="Project 2"),
        ]

        with (
            patch("auto_slopp.utils.openproject_operations._get_api_client") as mock_client,
            patch("auto_slopp.utils.openproject_operations.settings"),
        ):
            mock_api_client = MagicMock()
            mock_api_client.__enter__ = MagicMock(return_value=mock_api_client)
            mock_api_client.__exit__ = MagicMock(return_value=False)

            def serialize(x):
                return {"identifier": x.identifier, "name": x.name}

            mock_api_client.sanitize_for_serialization.side_effect = serialize
            mock_client.return_value = mock_api_client

            with (patch("auto_slopp.utils.openproject_operations.ProjectsApi") as mock_projects_api,):
                mock_api_instance = MagicMock()
                mock_api_instance.list_projects.return_value = mock_result
                mock_projects_api.return_value = mock_api_instance

                projects = get_projects()

                assert len(projects) == 2
                assert projects[0]["name"] == "Project 1"

    def test_get_projects_empty(self):
        """Test retrieval when no projects exist."""
        mock_result = MagicMock()
        mock_result._embedded = MagicMock()
        mock_result._embedded.elements = []

        with (
            patch("auto_slopp.utils.openproject_operations._get_api_client") as mock_client,
            patch("auto_slopp.utils.openproject_operations.settings"),
        ):
            mock_api_client = MagicMock()
            mock_api_client.__enter__ = MagicMock(return_value=mock_api_client)
            mock_api_client.__exit__ = MagicMock(return_value=False)
            mock_client.return_value = mock_api_client

            with (patch("auto_slopp.utils.openproject_operations.ProjectsApi") as mock_projects_api,):
                mock_api_instance = MagicMock()
                mock_api_instance.list_projects.return_value = mock_result
                mock_projects_api.return_value = mock_api_instance

                projects = get_projects()

                assert projects == []

    def test_get_projects_api_error(self):
        """Test handling of API errors."""
        from openproject.openapi_client.openproject_client.exceptions import (
            ApiException,
        )

        with (
            patch("auto_slopp.utils.openproject_operations._get_api_client") as mock_client,
            patch("auto_slopp.utils.openproject_operations.settings"),
        ):
            mock_api_client = MagicMock()
            mock_api_client.__enter__ = MagicMock(return_value=mock_api_client)
            mock_api_client.__exit__ = MagicMock(return_value=False)
            mock_client.return_value = mock_api_client

            with (patch("auto_slopp.utils.openproject_operations.ProjectsApi") as mock_projects_api,):
                mock_api_instance = MagicMock()
                mock_api_instance.list_projects.side_effect = ApiException("Connection failed")
                mock_projects_api.return_value = mock_api_instance

                projects = get_projects()

                assert projects == []


class TestGetProjectByIdentifier:
    """Tests for get_project_by_identifier function."""

    def test_get_project_by_identifier_found(self):
        """Test finding project by identifier."""
        mock_result = MagicMock()
        mock_result._embedded = MagicMock()
        mock_result._embedded.elements = [
            MockElement(identifier="test_project", name="Test Project"),
        ]

        with (
            patch("auto_slopp.utils.openproject_operations._get_api_client") as mock_client,
            patch("auto_slopp.utils.openproject_operations.settings"),
        ):
            mock_api_client = MagicMock()
            mock_api_client.__enter__ = MagicMock(return_value=mock_api_client)
            mock_api_client.__exit__ = MagicMock(return_value=False)

            def serialize(x):
                return {"identifier": x.identifier, "name": x.name}

            mock_api_client.sanitize_for_serialization.side_effect = serialize
            mock_client.return_value = mock_api_client

            with (patch("auto_slopp.utils.openproject_operations.ProjectsApi") as mock_projects_api,):
                mock_api_instance = MagicMock()
                mock_api_instance.list_projects.return_value = mock_result
                mock_projects_api.return_value = mock_api_instance

                project = get_project_by_identifier("test_project")

                assert project is not None
                assert project["identifier"] == "test_project"
                mock_api_instance.list_projects.assert_called_once_with()

    def test_get_project_by_identifier_found_among_multiple(self):
        """Test finding project by identifier among multiple projects."""
        mock_result = MagicMock()
        mock_result._embedded = MagicMock()
        mock_result._embedded.elements = [
            MockElement(identifier="other_project", name="Other Project"),
            MockElement(identifier="test_project", name="Test Project"),
            MockElement(identifier="another_project", name="Another Project"),
        ]

        with (
            patch("auto_slopp.utils.openproject_operations._get_api_client") as mock_client,
            patch("auto_slopp.utils.openproject_operations.settings"),
        ):
            mock_api_client = MagicMock()
            mock_api_client.__enter__ = MagicMock(return_value=mock_api_client)
            mock_api_client.__exit__ = MagicMock(return_value=False)

            def serialize(x):
                return {"identifier": x.identifier, "name": x.name}

            mock_api_client.sanitize_for_serialization.side_effect = serialize
            mock_client.return_value = mock_api_client

            with (patch("auto_slopp.utils.openproject_operations.ProjectsApi") as mock_projects_api,):
                mock_api_instance = MagicMock()
                mock_api_instance.list_projects.return_value = mock_result
                mock_projects_api.return_value = mock_api_instance

                project = get_project_by_identifier("test_project")

                assert project is not None
                assert project["identifier"] == "test_project"
                assert project["name"] == "Test Project"

    def test_get_project_by_identifier_not_found(self):
        """Test when project not found by identifier."""
        mock_result = MagicMock()
        mock_result._embedded = MagicMock()
        mock_result._embedded.elements = []

        with (
            patch("auto_slopp.utils.openproject_operations._get_api_client") as mock_client,
            patch("auto_slopp.utils.openproject_operations.settings"),
        ):
            mock_api_client = MagicMock()
            mock_api_client.__enter__ = MagicMock(return_value=mock_api_client)
            mock_api_client.__exit__ = MagicMock(return_value=False)
            mock_client.return_value = mock_api_client

            with (patch("auto_slopp.utils.openproject_operations.ProjectsApi") as mock_projects_api,):
                mock_api_instance = MagicMock()
                mock_api_instance.list_projects.return_value = mock_result
                mock_projects_api.return_value = mock_api_instance

                project = get_project_by_identifier("nonexistent")

                assert project is None
                mock_api_instance.list_projects.assert_called_once_with()


class TestGetProjectByName:
    """Tests for get_project_by_name function."""

    def test_get_project_by_name_found(self):
        """Test finding project by name."""
        mock_result = MagicMock()
        mock_result._embedded = MagicMock()
        mock_result._embedded.elements = [
            MockElement(identifier="test", name="Test Project"),
        ]

        with (
            patch("auto_slopp.utils.openproject_operations._get_api_client") as mock_client,
            patch("auto_slopp.utils.openproject_operations.settings"),
        ):
            mock_api_client = MagicMock()
            mock_api_client.__enter__ = MagicMock(return_value=mock_api_client)
            mock_api_client.__exit__ = MagicMock(return_value=False)

            def serialize(x):
                return {"identifier": x.identifier, "name": x.name}

            mock_api_client.sanitize_for_serialization.side_effect = serialize
            mock_client.return_value = mock_api_client

            with (patch("auto_slopp.utils.openproject_operations.ProjectsApi") as mock_projects_api,):
                mock_api_instance = MagicMock()
                mock_api_instance.list_projects.return_value = mock_result
                mock_projects_api.return_value = mock_api_instance

                project = get_project_by_name("Test Project")

                assert project is not None
                assert project["name"] == "Test Project"
                expected_filter = '[{"name":{"operator":"~","values":["Test Project"]}}]'
                mock_api_instance.list_projects.assert_called_once_with(filters=expected_filter)

    def test_get_project_by_name_not_found(self):
        """Test when project not found by name."""
        mock_result = MagicMock()
        mock_result._embedded = MagicMock()
        mock_result._embedded.elements = []

        with (
            patch("auto_slopp.utils.openproject_operations._get_api_client") as mock_client,
            patch("auto_slopp.utils.openproject_operations.settings"),
        ):
            mock_api_client = MagicMock()
            mock_api_client.__enter__ = MagicMock(return_value=mock_api_client)
            mock_api_client.__exit__ = MagicMock(return_value=False)
            mock_client.return_value = mock_api_client

            with (patch("auto_slopp.utils.openproject_operations.ProjectsApi") as mock_projects_api,):
                mock_api_instance = MagicMock()
                mock_api_instance.list_projects.return_value = mock_result
                mock_projects_api.return_value = mock_api_instance

                project = get_project_by_name("Nonexistent Project")

                assert project is None
                expected_filter = '[{"name":{"operator":"~","values":["Nonexistent Project"]}}]'
                mock_api_instance.list_projects.assert_called_once_with(filters=expected_filter)


class TestCreateProject:
    """Tests for create_project function."""

    def test_create_project_success(self):
        """Test successful project creation."""
        mock_result = MockElement(id=1, name="New Project", identifier="new_project")

        with (
            patch("auto_slopp.utils.openproject_operations._get_api_client") as mock_client,
            patch("auto_slopp.utils.openproject_operations.settings"),
        ):
            mock_api_client = MagicMock()
            mock_api_client.__enter__ = MagicMock(return_value=mock_api_client)
            mock_api_client.__exit__ = MagicMock(return_value=False)
            mock_api_client.sanitize_for_serialization.return_value = {
                "id": 1,
                "name": "New Project",
                "identifier": "new_project",
            }
            mock_client.return_value = mock_api_client

            with (
                patch("auto_slopp.utils.openproject_operations.ProjectsApi") as mock_projects_api,
                patch("auto_slopp.utils.openproject_operations.ProjectModel") as mock_model,
            ):
                mock_api_instance = MagicMock()
                mock_api_instance.create_project.return_value = mock_result
                mock_projects_api.return_value = mock_api_instance

                project = create_project(
                    name="New Project",
                    identifier="new_project",
                    description="Project description",
                )

                assert project is not None
                assert project["name"] == "New Project"
                mock_api_instance.create_project.assert_called_once()

    def test_create_project_without_description(self):
        """Test project creation without description."""
        mock_result = MockElement(id=1, name="New Project", identifier="new_project")

        with (
            patch("auto_slopp.utils.openproject_operations._get_api_client") as mock_client,
            patch("auto_slopp.utils.openproject_operations.settings"),
        ):
            mock_api_client = MagicMock()
            mock_api_client.__enter__ = MagicMock(return_value=mock_api_client)
            mock_api_client.__exit__ = MagicMock(return_value=False)
            mock_api_client.sanitize_for_serialization.return_value = {
                "id": 1,
                "name": "New Project",
                "identifier": "new_project",
            }
            mock_client.return_value = mock_api_client

            with (
                patch("auto_slopp.utils.openproject_operations.ProjectsApi") as mock_projects_api,
                patch("auto_slopp.utils.openproject_operations.ProjectModel") as mock_model,
            ):
                mock_api_instance = MagicMock()
                mock_api_instance.create_project.return_value = mock_result
                mock_projects_api.return_value = mock_api_instance

                project = create_project(name="New Project", identifier="new_project")

                assert project is not None

    def test_create_project_description_includes_format(self):
        """Test that description includes format field for ProjectModel validation."""
        project_data = {
            "name": "Test Project",
            "identifier": "test_project",
            "description": {"format": "markdown", "raw": "Test description"},
        }

        project_model = ProjectModel(**project_data)
        assert project_model.description is not None
        assert project_model.description.format == "markdown"
        assert project_model.description.raw == "Test description"

    def test_create_project_description_missing_format_fails(self):
        """Test that description without format field fails validation."""
        project_data = {
            "name": "Test Project",
            "identifier": "test_project",
            "description": {"raw": "Test description"},
        }

        with pytest.raises(ValidationError) as exc_info:
            ProjectModel(**project_data)

        assert "format" in str(exc_info.value)
        assert "Field required" in str(exc_info.value)


class TestGetWorkPackages:
    """Tests for get_work_packages function."""

    def test_get_work_packages_success(self):
        """Test successful retrieval of work packages."""
        mock_result = MagicMock()
        mock_result._embedded = MagicMock()
        mock_result._embedded.elements = [
            MockElement(id=1, subject="Task 1"),
            MockElement(id=2, subject="Task 2"),
        ]

        with (
            patch("auto_slopp.utils.openproject_operations._get_api_client") as mock_client,
            patch("auto_slopp.utils.openproject_operations.settings"),
        ):
            mock_api_client = MagicMock()
            mock_api_client.__enter__ = MagicMock(return_value=mock_api_client)
            mock_api_client.__exit__ = MagicMock(return_value=False)

            def serialize(x):
                return {"id": x.id, "subject": x.subject}

            mock_api_client.sanitize_for_serialization.side_effect = serialize
            mock_client.return_value = mock_api_client

            with (patch("auto_slopp.utils.openproject_operations.WorkPackagesApi") as mock_wp_api,):
                mock_api_instance = MagicMock()
                mock_api_instance.list_work_packages.return_value = mock_result
                mock_wp_api.return_value = mock_api_instance

                work_packages = get_work_packages(project_id=1)

                assert len(work_packages) == 2
                assert work_packages[0]["subject"] == "Task 1"


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
        mock_result = MockElement(id=1, subject="Test Task")

        with (
            patch("auto_slopp.utils.openproject_operations._get_api_client") as mock_client,
            patch("auto_slopp.utils.openproject_operations.settings"),
        ):
            mock_api_client = MagicMock()
            mock_api_client.__enter__ = MagicMock(return_value=mock_api_client)
            mock_api_client.__exit__ = MagicMock(return_value=False)
            mock_api_client.sanitize_for_serialization.return_value = {
                "id": 1,
                "subject": "Test Task",
            }
            mock_client.return_value = mock_api_client

            with (patch("auto_slopp.utils.openproject_operations.WorkPackagesApi") as mock_wp_api,):
                mock_api_instance = MagicMock()
                mock_api_instance.view_work_package.return_value = mock_result
                mock_wp_api.return_value = mock_api_instance

                wp = get_work_package(1)

                assert wp is not None
                assert wp["id"] == 1

    def test_get_work_package_not_found(self):
        """Test when work package not found."""
        from openproject.openapi_client.openproject_client.exceptions import (
            ApiException,
        )

        with (
            patch("auto_slopp.utils.openproject_operations._get_api_client") as mock_client,
            patch("auto_slopp.utils.openproject_operations.settings"),
        ):
            mock_api_client = MagicMock()
            mock_api_client.__enter__ = MagicMock(return_value=mock_api_client)
            mock_api_client.__exit__ = MagicMock(return_value=False)
            mock_client.return_value = mock_api_client

            with (patch("auto_slopp.utils.openproject_operations.WorkPackagesApi") as mock_wp_api,):
                mock_api_instance = MagicMock()
                mock_api_instance.view_work_package.side_effect = ApiException("Not found")
                mock_wp_api.return_value = mock_api_instance

                wp = get_work_package(999)

                assert wp is None


class TestCreateWorkPackage:
    """Tests for create_work_package function."""

    def test_create_work_package_success(self):
        """Test successful work package creation."""
        mock_result = MockElement(id=1, subject="New Task")

        with (
            patch("auto_slopp.utils.openproject_operations._get_api_client") as mock_client,
            patch("auto_slopp.utils.openproject_operations.settings"),
        ):
            mock_api_client = MagicMock()
            mock_api_client.__enter__ = MagicMock(return_value=mock_api_client)
            mock_api_client.__exit__ = MagicMock(return_value=False)
            mock_api_client.sanitize_for_serialization.return_value = {
                "id": 1,
                "subject": "New Task",
            }
            mock_client.return_value = mock_api_client

            with (
                patch("auto_slopp.utils.openproject_operations.WorkPackagesApi") as mock_wp_api,
                patch("auto_slopp.utils.openproject_operations.WorkPackageWriteModel") as mock_model,
            ):
                mock_api_instance = MagicMock()
                mock_api_instance.create_work_package.return_value = mock_result
                mock_wp_api.return_value = mock_api_instance

                wp = create_work_package(
                    project_id=1,
                    subject="New Task",
                    description="Task description",
                )

                assert wp is not None
                assert wp["subject"] == "New Task"


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
        mock_result = MockElement(id=1, subject="Updated Task")

        with (
            patch("auto_slopp.utils.openproject_operations._get_api_client") as mock_client,
            patch("auto_slopp.utils.openproject_operations.settings"),
        ):
            mock_api_client = MagicMock()
            mock_api_client.__enter__ = MagicMock(return_value=mock_api_client)
            mock_api_client.__exit__ = MagicMock(return_value=False)
            mock_api_client.sanitize_for_serialization.return_value = {
                "id": 1,
                "subject": "Updated Task",
            }
            mock_client.return_value = mock_api_client

            with (
                patch("auto_slopp.utils.openproject_operations.WorkPackagesApi") as mock_wp_api,
                patch("auto_slopp.utils.openproject_operations.WorkPackagePatchModel") as mock_model,
            ):
                mock_api_instance = MagicMock()
                mock_api_instance.update_work_package.return_value = mock_result
                mock_wp_api.return_value = mock_api_instance

                wp = update_work_package(
                    work_package_id=1,
                    lock_version=1,
                    status_id=7,
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
        with (
            patch("auto_slopp.utils.openproject_operations._get_api_client") as mock_client,
            patch("auto_slopp.utils.openproject_operations.settings"),
        ):
            mock_api_client = MagicMock()
            mock_api_client.__enter__ = MagicMock(return_value=mock_api_client)
            mock_api_client.__exit__ = MagicMock(return_value=False)
            mock_client.return_value = mock_api_client

            with (
                patch("auto_slopp.utils.openproject_operations.WorkPackagesApi") as mock_wp_api,
                patch("auto_slopp.utils.openproject_operations.ActivityCommentWriteModel") as mock_model,
            ):
                mock_api_instance = MagicMock()
                mock_wp_api.return_value = mock_api_instance

                result = add_comment_to_work_package(
                    work_package_id=1,
                    comment="This is a comment",
                )

                assert result is True

    def test_add_comment_failure(self):
        """Test handling failure when adding comment."""
        from openproject.openapi_client.openproject_client.exceptions import (
            ApiException,
        )

        with (
            patch("auto_slopp.utils.openproject_operations._get_api_client") as mock_client,
            patch("auto_slopp.utils.openproject_operations.settings"),
        ):
            mock_api_client = MagicMock()
            mock_api_client.__enter__ = MagicMock(return_value=mock_api_client)
            mock_api_client.__exit__ = MagicMock(return_value=False)
            mock_client.return_value = mock_api_client

            with (
                patch("auto_slopp.utils.openproject_operations.WorkPackagesApi") as mock_wp_api,
                patch("auto_slopp.utils.openproject_operations.ActivityCommentWriteModel") as mock_model,
            ):
                mock_api_instance = MagicMock()
                mock_api_instance.create_work_package_activity.side_effect = ApiException("Failed")
                mock_wp_api.return_value = mock_api_instance

                result = add_comment_to_work_package(
                    work_package_id=1,
                    comment="This is a comment",
                )

                assert result is False


class TestGetAvailableStatuses:
    """Tests for get_available_statuses function."""

    def test_get_available_statuses_success(self):
        """Test successful retrieval of statuses."""
        mock_result = MagicMock()
        mock_result._embedded = MagicMock()
        mock_result._embedded.elements = [
            MockElement(id=1, name="New"),
            MockElement(id=7, name="In Progress"),
        ]

        with (
            patch("auto_slopp.utils.openproject_operations._get_api_client") as mock_client,
            patch("auto_slopp.utils.openproject_operations.settings"),
        ):
            mock_api_client = MagicMock()
            mock_api_client.__enter__ = MagicMock(return_value=mock_api_client)
            mock_api_client.__exit__ = MagicMock(return_value=False)

            def serialize(x):
                return {"id": x.id, "name": x.name}

            mock_api_client.sanitize_for_serialization.side_effect = serialize
            mock_client.return_value = mock_api_client

            with (patch("auto_slopp.utils.openproject_operations.StatusesApi") as mock_statuses_api,):
                mock_api_instance = MagicMock()
                mock_api_instance.list_available_statuses_for_project.return_value = mock_result
                mock_statuses_api.return_value = mock_api_instance

                statuses = get_available_statuses(project_id=1)

                assert len(statuses) == 2
                assert statuses[0]["name"] == "New"


class TestGetUser:
    """Tests for get_user function."""

    def test_get_user_found(self):
        """Test finding a user by ID."""
        mock_result = MockElement(id=1, name="Test User")

        with (
            patch("auto_slopp.utils.openproject_operations._get_api_client") as mock_client,
            patch("auto_slopp.utils.openproject_operations.settings"),
        ):
            mock_api_client = MagicMock()
            mock_api_client.__enter__ = MagicMock(return_value=mock_api_client)
            mock_api_client.__exit__ = MagicMock(return_value=False)
            mock_api_client.sanitize_for_serialization.return_value = {
                "id": 1,
                "name": "Test User",
            }
            mock_client.return_value = mock_api_client

            with (patch("auto_slopp.utils.openproject_operations.UsersApi") as mock_users_api,):
                mock_api_instance = MagicMock()
                mock_api_instance.view_user.return_value = mock_result
                mock_users_api.return_value = mock_api_instance

                user = get_user(1)

                assert user is not None
                assert user["name"] == "Test User"


class TestGetCurrentUser:
    """Tests for get_current_user function."""

    def test_get_current_user_success(self):
        """Test getting current user."""
        mock_result = MockElement(id=1, name="Current User")

        with (
            patch("auto_slopp.utils.openproject_operations._get_api_client") as mock_client,
            patch("auto_slopp.utils.openproject_operations.settings"),
        ):
            mock_api_client = MagicMock()
            mock_api_client.__enter__ = MagicMock(return_value=mock_api_client)
            mock_api_client.__exit__ = MagicMock(return_value=False)
            mock_api_client.sanitize_for_serialization.return_value = {
                "id": 1,
                "name": "Current User",
            }
            mock_client.return_value = mock_api_client

            with (patch("auto_slopp.utils.openproject_operations.UsersApi") as mock_users_api,):
                mock_api_instance = MagicMock()
                mock_api_instance.view_current_user.return_value = mock_result
                mock_users_api.return_value = mock_api_instance

                user = get_current_user()

                assert user is not None
                assert user["name"] == "Current User"


class TestGetWorkPackageTypes:
    """Tests for get_work_package_types function."""

    def test_get_work_package_types_success(self):
        """Test successful retrieval of work package types."""
        mock_result = MagicMock()
        mock_result._embedded = MagicMock()
        mock_result._embedded.elements = [
            MockElement(id=1, name="Task"),
            MockElement(id=2, name="Feature"),
        ]

        with (
            patch("auto_slopp.utils.openproject_operations._get_api_client") as mock_client,
            patch("auto_slopp.utils.openproject_operations.settings"),
        ):
            mock_api_client = MagicMock()
            mock_api_client.__enter__ = MagicMock(return_value=mock_api_client)
            mock_api_client.__exit__ = MagicMock(return_value=False)

            def serialize(x):
                return {"id": x.id, "name": x.name}

            mock_api_client.sanitize_for_serialization.side_effect = serialize
            mock_client.return_value = mock_api_client

            with (patch("auto_slopp.utils.openproject_operations.TypesApi") as mock_types_api,):
                mock_api_instance = MagicMock()
                mock_api_instance.list_types_for_project.return_value = mock_result
                mock_types_api.return_value = mock_api_instance

                types = get_work_package_types(project_id=1)

                assert len(types) == 2
                assert types[0]["name"] == "Task"


class TestOpenProjectOperationError:
    """Tests for OpenProjectOperationError exception."""

    def test_error_message(self):
        """Test that error message is preserved."""
        error = OpenProjectOperationError("Test error message")
        assert str(error) == "Test error message"


class TestCreateWorkPackageWithAllParams:
    """Tests for create_work_package with all optional parameters."""

    def test_create_work_package_with_all_params(self):
        """Test work package creation with all optional parameters."""
        mock_result = MockElement(id=1, subject="Full Task")

        with (
            patch("auto_slopp.utils.openproject_operations._get_api_client") as mock_client,
            patch("auto_slopp.utils.openproject_operations.settings"),
        ):
            mock_api_client = MagicMock()
            mock_api_client.__enter__ = MagicMock(return_value=mock_api_client)
            mock_api_client.__exit__ = MagicMock(return_value=False)
            mock_api_client.sanitize_for_serialization.return_value = {
                "id": 1,
                "subject": "Full Task",
            }
            mock_client.return_value = mock_api_client

            with (
                patch("auto_slopp.utils.openproject_operations.WorkPackagesApi") as mock_wp_api,
                patch("auto_slopp.utils.openproject_operations.WorkPackageWriteModel") as mock_model,
            ):
                mock_api_instance = MagicMock()
                mock_api_instance.create_work_package.return_value = mock_result
                mock_wp_api.return_value = mock_api_instance

                wp = create_work_package(
                    project_id=1,
                    subject="Full Task",
                    description="Full description",
                    type_id=2,
                    parent_id=10,
                    assignee_id=5,
                )

                assert wp is not None
                assert wp["subject"] == "Full Task"
                mock_api_instance.create_work_package.assert_called_once()


class TestUpdateWorkPackageWithMultipleParams:
    """Tests for update_work_package with multiple parameters."""

    def test_update_work_package_with_assignee(self):
        """Test updating work package with assignee."""
        mock_result = MockElement(id=1, subject="Updated Task")

        with (
            patch("auto_slopp.utils.openproject_operations._get_api_client") as mock_client,
            patch("auto_slopp.utils.openproject_operations.settings"),
        ):
            mock_api_client = MagicMock()
            mock_api_client.__enter__ = MagicMock(return_value=mock_api_client)
            mock_api_client.__exit__ = MagicMock(return_value=False)
            mock_api_client.sanitize_for_serialization.return_value = {
                "id": 1,
                "subject": "Updated Task",
            }
            mock_client.return_value = mock_api_client

            with (
                patch("auto_slopp.utils.openproject_operations.WorkPackagesApi") as mock_wp_api,
                patch("auto_slopp.utils.openproject_operations.WorkPackagePatchModel") as mock_model,
            ):
                mock_api_instance = MagicMock()
                mock_api_instance.update_work_package.return_value = mock_result
                mock_wp_api.return_value = mock_api_instance

                wp = update_work_package(
                    work_package_id=1,
                    lock_version=1,
                    assignee_id=5,
                )

                assert wp is not None

    def test_update_work_package_with_description_and_subject(self):
        """Test updating work package with description and subject."""
        mock_result = MockElement(id=1, subject="New Subject")

        with (
            patch("auto_slopp.utils.openproject_operations._get_api_client") as mock_client,
            patch("auto_slopp.utils.openproject_operations.settings"),
        ):
            mock_api_client = MagicMock()
            mock_api_client.__enter__ = MagicMock(return_value=mock_api_client)
            mock_api_client.__exit__ = MagicMock(return_value=False)
            mock_api_client.sanitize_for_serialization.return_value = {
                "id": 1,
                "subject": "New Subject",
            }
            mock_client.return_value = mock_api_client

            with (
                patch("auto_slopp.utils.openproject_operations.WorkPackagesApi") as mock_wp_api,
                patch("auto_slopp.utils.openproject_operations.WorkPackagePatchModel") as mock_model,
            ):
                mock_api_instance = MagicMock()
                mock_api_instance.update_work_package.return_value = mock_result
                mock_wp_api.return_value = mock_api_instance

                wp = update_work_package(
                    work_package_id=1,
                    lock_version=1,
                    description="New description",
                    subject="New Subject",
                )

                assert wp is not None


class TestGenericExceptionHandling:
    """Tests for generic exception handling."""

    def test_get_projects_generic_exception(self):
        """Test handling of generic exceptions in get_projects."""
        with (
            patch("auto_slopp.utils.openproject_operations._get_api_client") as mock_client,
            patch("auto_slopp.utils.openproject_operations.settings"),
        ):
            mock_api_client = MagicMock()
            mock_api_client.__enter__ = MagicMock(side_effect=ValueError("Unexpected error"))
            mock_api_client.__exit__ = MagicMock(return_value=False)
            mock_client.return_value = mock_api_client

            projects = get_projects()

            assert projects == []

    def test_get_work_package_generic_exception(self):
        """Test handling of generic exceptions in get_work_package."""
        with (
            patch("auto_slopp.utils.openproject_operations._get_api_client") as mock_client,
            patch("auto_slopp.utils.openproject_operations.settings"),
        ):
            mock_api_client = MagicMock()
            mock_api_client.__enter__ = MagicMock(side_effect=RuntimeError("Unexpected error"))
            mock_api_client.__exit__ = MagicMock(return_value=False)
            mock_client.return_value = mock_api_client

            wp = get_work_package(1)

            assert wp is None

    def test_get_user_generic_exception(self):
        """Test handling of generic exceptions in get_user."""
        with (
            patch("auto_slopp.utils.openproject_operations._get_api_client") as mock_client,
            patch("auto_slopp.utils.openproject_operations.settings"),
        ):
            mock_api_client = MagicMock()
            mock_api_client.__enter__ = MagicMock(side_effect=KeyError("Unexpected error"))
            mock_api_client.__exit__ = MagicMock(return_value=False)
            mock_client.return_value = mock_api_client

            user = get_user(1)

            assert user is None

    def test_add_comment_generic_exception(self):
        """Test handling of generic exceptions in add_comment_to_work_package."""
        with (
            patch("auto_slopp.utils.openproject_operations._get_api_client") as mock_client,
            patch("auto_slopp.utils.openproject_operations.settings"),
        ):
            mock_api_client = MagicMock()
            mock_api_client.__enter__ = MagicMock(side_effect=TypeError("Unexpected error"))
            mock_api_client.__exit__ = MagicMock(return_value=False)
            mock_client.return_value = mock_api_client

            result = add_comment_to_work_package(work_package_id=1, comment="Test")

            assert result is False


class TestGetWorkPackagesWithFilters:
    """Tests for get_work_packages with various filters."""

    def test_get_work_packages_with_assigned_user_filter(self):
        """Test work packages retrieval with user filter."""
        mock_result = MagicMock()
        mock_result._embedded = MagicMock()
        mock_result._embedded.elements = [
            MockElement(id=1, subject="Assigned Task"),
        ]

        with (
            patch("auto_slopp.utils.openproject_operations._get_api_client") as mock_client,
            patch("auto_slopp.utils.openproject_operations.settings"),
        ):
            mock_api_client = MagicMock()
            mock_api_client.__enter__ = MagicMock(return_value=mock_api_client)
            mock_api_client.__exit__ = MagicMock(return_value=False)

            def serialize(x):
                return {"id": x.id, "subject": x.subject}

            mock_api_client.sanitize_for_serialization.side_effect = serialize
            mock_client.return_value = mock_api_client

            with patch("auto_slopp.utils.openproject_operations.WorkPackagesApi") as mock_wp_api:
                mock_api_instance = MagicMock()
                mock_api_instance.list_work_packages.return_value = mock_result
                mock_wp_api.return_value = mock_api_instance

                work_packages = get_work_packages(
                    project_id=1,
                    assigned_to_user_id=5,
                )

                assert len(work_packages) == 1
                assert work_packages[0]["subject"] == "Assigned Task"

    def test_get_work_packages_with_status_filter(self):
        """Test work packages retrieval with status filter."""
        mock_result = MagicMock()
        mock_result._embedded = MagicMock()
        mock_result._embedded.elements = [
            MockElement(id=2, subject="Filtered Task"),
        ]

        with (
            patch("auto_slopp.utils.openproject_operations._get_api_client") as mock_client,
            patch("auto_slopp.utils.openproject_operations.settings"),
        ):
            mock_api_client = MagicMock()
            mock_api_client.__enter__ = MagicMock(return_value=mock_api_client)
            mock_api_client.__exit__ = MagicMock(return_value=False)

            def serialize(x):
                return {"id": x.id, "subject": x.subject}

            mock_api_client.sanitize_for_serialization.side_effect = serialize
            mock_client.return_value = mock_api_client

            with patch("auto_slopp.utils.openproject_operations.WorkPackagesApi") as mock_wp_api:
                mock_api_instance = MagicMock()
                mock_api_instance.list_work_packages.return_value = mock_result
                mock_wp_api.return_value = mock_api_instance

                work_packages = get_work_packages(
                    project_id=1,
                    status_id=7,
                )

                assert len(work_packages) == 1
                assert work_packages[0]["subject"] == "Filtered Task"
