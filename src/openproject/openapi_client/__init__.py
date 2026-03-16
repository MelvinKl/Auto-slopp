"""OpenAPI client for OpenProject."""

import sys
from pathlib import Path

client_path = Path(__file__).parent
if str(client_path) not in sys.path:
    sys.path.insert(0, str(client_path))

from openproject_client import (
    ActivitiesApi,
    ActivityCommentWriteModel,
    ApiClient,
    ApiException,
    Configuration,
    ProjectModel,
    ProjectsApi,
    StatusesApi,
    TypesApi,
    UsersApi,
    WorkPackageModel,
    WorkPackagePatchModel,
    WorkPackageWriteModel,
    WorkPackagesApi,
)

__all__ = [
    "ActivitiesApi",
    "ActivityCommentWriteModel",
    "ApiClient",
    "ApiException",
    "Configuration",
    "ProjectModel",
    "ProjectsApi",
    "StatusesApi",
    "TypesApi",
    "UsersApi",
    "WorkPackageModel",
    "WorkPackagePatchModel",
    "WorkPackageWriteModel",
    "WorkPackagesApi",
]
