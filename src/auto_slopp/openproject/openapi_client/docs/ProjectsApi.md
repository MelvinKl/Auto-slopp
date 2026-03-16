# auto_slopp.openproject.openapi_client.ProjectsApi

All URIs are relative to *https://openproject.melvin.beer*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_project**](ProjectsApi.md#create_project) | **POST** /api/v3/projects | Create project
[**create_project_copy**](ProjectsApi.md#create_project_copy) | **POST** /api/v3/projects/{id}/copy | Create project copy
[**delete_project**](ProjectsApi.md#delete_project) | **DELETE** /api/v3/projects/{id} | Delete Project
[**favorite_project**](ProjectsApi.md#favorite_project) | **POST** /api/v3/projects/{id}/favorite | Favorite Project
[**list_available_parent_project_candidates**](ProjectsApi.md#list_available_parent_project_candidates) | **GET** /api/v3/projects/available_parent_projects | List available parent project candidates
[**list_projects**](ProjectsApi.md#list_projects) | **GET** /api/v3/projects | List projects
[**list_projects_with_version**](ProjectsApi.md#list_projects_with_version) | **GET** /api/v3/versions/{id}/projects | List projects having version
[**list_workspaces_with_version**](ProjectsApi.md#list_workspaces_with_version) | **GET** /api/v3/versions/{id}/workspaces | List workspaces having version
[**project_copy_form**](ProjectsApi.md#project_copy_form) | **POST** /api/v3/projects/{id}/copy/form | Project copy form
[**project_create_form**](ProjectsApi.md#project_create_form) | **POST** /api/v3/projects/form | Project create form
[**project_update_form**](ProjectsApi.md#project_update_form) | **POST** /api/v3/projects/{id}/form | Project update form
[**unfavorite_project**](ProjectsApi.md#unfavorite_project) | **DELETE** /api/v3/projects/{id}/favorite | Unfavorite Project
[**update_project**](ProjectsApi.md#update_project) | **PATCH** /api/v3/projects/{id} | Update Project
[**view_project**](ProjectsApi.md#view_project) | **GET** /api/v3/projects/{id} | View project
[**view_project_configuration**](ProjectsApi.md#view_project_configuration) | **GET** /api/v3/projects/{id}/configuration | View project configuration
[**view_project_schema**](ProjectsApi.md#view_project_schema) | **GET** /api/v3/projects/schema | View project schema
[**view_project_status**](ProjectsApi.md#view_project_status) | **GET** /api/v3/project_statuses/{id} | View project status


# **create_project**
> ProjectModel create_project(project_model=project_model)

Create project

Creates a new project, applying the attributes provided in the body.

You can use the form and schema to be retrieve the valid attribute values and by that be guided towards successful creation.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.project_model import ProjectModel
from auto_slopp.openproject.openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://openproject.melvin.beer
# See configuration.py for a list of all supported configuration parameters.
configuration = auto_slopp.openproject.openapi_client.Configuration(
    host = "https://openproject.melvin.beer"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure HTTP basic authorization: BasicAuth
configuration = auto_slopp.openproject.openapi_client.Configuration(
    username = os.environ["USERNAME"],
    password = os.environ["PASSWORD"]
)

# Enter a context with an instance of the API client
with auto_slopp.openproject.openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = auto_slopp.openproject.openapi_client.ProjectsApi(api_client)
    project_model = auto_slopp.openproject.openapi_client.ProjectModel() # ProjectModel |  (optional)

    try:
        # Create project
        api_response = api_instance.create_project(project_model=project_model)
        print("The response of ProjectsApi->create_project:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProjectsApi->create_project: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_model** | [**ProjectModel**](ProjectModel.md)|  | [optional] 

### Return type

[**ProjectModel**](ProjectModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/hal+json, text/plain

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Created |  -  |
**400** | Occurs when the client did not send a valid JSON object in the request body. |  -  |
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** add project which is a global permission |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |
**422** | Returned if:  * a constraint for a property was violated (&#x60;PropertyConstraintViolation&#x60;) |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_project_copy**
> create_project_copy(id)

Create project copy



### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://openproject.melvin.beer
# See configuration.py for a list of all supported configuration parameters.
configuration = auto_slopp.openproject.openapi_client.Configuration(
    host = "https://openproject.melvin.beer"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure HTTP basic authorization: BasicAuth
configuration = auto_slopp.openproject.openapi_client.Configuration(
    username = os.environ["USERNAME"],
    password = os.environ["PASSWORD"]
)

# Enter a context with an instance of the API client
with auto_slopp.openproject.openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = auto_slopp.openproject.openapi_client.ProjectsApi(api_client)
    id = 1 # int | Project id

    try:
        # Create project copy
        api_instance.create_project_copy(id)
    except Exception as e:
        print("Exception when calling ProjectsApi->create_project_copy: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Project id | 

### Return type

void (empty response body)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json, text/plain

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**302** | Returned if the request is successful. It will redirect to the job statuses API with the backend job that got created. You can query that endpoint to check the status of the copy, and eventually get the created project. |  -  |
**400** | Occurs when the client did not send a valid JSON object in the request body. |  -  |
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** copy projects in the source project |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |
**422** | Returned if:  * a constraint for a property was violated (&#x60;PropertyConstraintViolation&#x60;) |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_project**
> delete_project(id)

Delete Project

Deletes the project permanently. As this is a lengthy process, the actual deletion is carried out asynchronously.
So the project might exist well after the request has returned successfully. To prevent unwanted changes to
the project scheduled for deletion, it is archived at once.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://openproject.melvin.beer
# See configuration.py for a list of all supported configuration parameters.
configuration = auto_slopp.openproject.openapi_client.Configuration(
    host = "https://openproject.melvin.beer"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure HTTP basic authorization: BasicAuth
configuration = auto_slopp.openproject.openapi_client.Configuration(
    username = os.environ["USERNAME"],
    password = os.environ["PASSWORD"]
)

# Enter a context with an instance of the API client
with auto_slopp.openproject.openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = auto_slopp.openproject.openapi_client.ProjectsApi(api_client)
    id = 1 # int | Project id

    try:
        # Delete Project
        api_instance.delete_project(id)
    except Exception as e:
        print("Exception when calling ProjectsApi->delete_project: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Project id | 

### Return type

void (empty response body)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json, text/plain

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | Returned if the project was successfully deleted. There is currently no endpoint to query for the actual deletion status. Such an endpoint _might_ be added in the future. |  -  |
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** admin |  -  |
**404** | Returned if the project does not exist or the client does not have sufficient permissions to see it.  **Required permission:** any permission in the project  *Note: A client without sufficient permissions shall not be able to test for the existence of a version. That&#39;s why a 404 is returned here, even if a 403 might be more appropriate.* |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |
**422** | Returned if the project cannot be deleted. This can happen when there are still references to the project in other workspaces that need to be severed at first. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **favorite_project**
> favorite_project(id)

Favorite Project

Adds the project to the current user's favorites.

This endpoint is deprecated and replaced by [`/api/v3/workspaces/{id}/favorite`](https://www.openproject.org/docs/api/endpoints/workspaces/#favorite-workspace)

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://openproject.melvin.beer
# See configuration.py for a list of all supported configuration parameters.
configuration = auto_slopp.openproject.openapi_client.Configuration(
    host = "https://openproject.melvin.beer"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure HTTP basic authorization: BasicAuth
configuration = auto_slopp.openproject.openapi_client.Configuration(
    username = os.environ["USERNAME"],
    password = os.environ["PASSWORD"]
)

# Enter a context with an instance of the API client
with auto_slopp.openproject.openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = auto_slopp.openproject.openapi_client.ProjectsApi(api_client)
    id = 1 # int | Project id

    try:
        # Favorite Project
        api_instance.favorite_project(id)
    except Exception as e:
        print("Exception when calling ProjectsApi->favorite_project: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Project id | 

### Return type

void (empty response body)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | Returned if the project was successfully added to favorites. |  -  |
**404** | Returned if the project does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view project |  -  |
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** logged in |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_available_parent_project_candidates**
> ListAvailableParentProjectCandidatesModel list_available_parent_project_candidates(filters=filters, of=of, workspace_type=workspace_type, sort_by=sort_by)

List available parent project candidates

Lists projects which can become parent to another project. Only sound candidates are returned.
For instance a project cannot become parent of itself or its children.

To specify the project for which a parent is queried for, the `of` parameter can be provided. If no `of`
parameter is provided, a new project is assumed. Then, the check for the hierarchy is omitted as a new project cannot be
part of a hierarchy yet, instead `workspace_type` parameter can be passed defining it for new project.

Candidates can be filtered. Most commonly one will want to filter by name or identifier.
You can do this through the `filters` parameter which works just like the work package index.

For instance to find all parent candidates with "rollout" in their name:

```
?filters=[{"name_and_identifier":{"operator":"~","values":["rollout"]}}]
```

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.list_available_parent_project_candidates_model import ListAvailableParentProjectCandidatesModel
from auto_slopp.openproject.openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://openproject.melvin.beer
# See configuration.py for a list of all supported configuration parameters.
configuration = auto_slopp.openproject.openapi_client.Configuration(
    host = "https://openproject.melvin.beer"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure HTTP basic authorization: BasicAuth
configuration = auto_slopp.openproject.openapi_client.Configuration(
    username = os.environ["USERNAME"],
    password = os.environ["PASSWORD"]
)

# Enter a context with an instance of the API client
with auto_slopp.openproject.openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = auto_slopp.openproject.openapi_client.ProjectsApi(api_client)
    filters = '[{ \"ancestor\": { \"operator\": \"=\", \"values\": [\'1\'] }\" }]' # str | JSON specifying filter conditions. (optional)
    of = '123' # str | The id or identifier of the project the parent candidate is determined for (optional)
    workspace_type = 'program' # str | The workspace type of the new project the parent candidate is determined for. Ignored when `of` parameter is provided. Note that while 'portfolio' is supported as a type (since it is a type of Workspace), the endpoint will currently always return an empty resultset as portfolios cannot have parents. (optional)
    sort_by = '[[\"id\", \"asc\"]]' # str | JSON specifying sort criteria. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint and allows all the filters and sortBy supported by the project list endpoint. (optional)

    try:
        # List available parent project candidates
        api_response = api_instance.list_available_parent_project_candidates(filters=filters, of=of, workspace_type=workspace_type, sort_by=sort_by)
        print("The response of ProjectsApi->list_available_parent_project_candidates:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProjectsApi->list_available_parent_project_candidates: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **filters** | **str**| JSON specifying filter conditions. | [optional] 
 **of** | **str**| The id or identifier of the project the parent candidate is determined for | [optional] 
 **workspace_type** | **str**| The workspace type of the new project the parent candidate is determined for. Ignored when &#x60;of&#x60; parameter is provided. Note that while &#39;portfolio&#39; is supported as a type (since it is a type of Workspace), the endpoint will currently always return an empty resultset as portfolios cannot have parents. | [optional] 
 **sort_by** | **str**| JSON specifying sort criteria. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint and allows all the filters and sortBy supported by the project list endpoint. | [optional] 

### Return type

[**ListAvailableParentProjectCandidatesModel**](ListAvailableParentProjectCandidatesModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** edit project in a project or the global add project permission |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_projects**
> ProjectCollectionModel list_projects(filters=filters, sort_by=sort_by, select=select)

List projects

Returns a collection of projects. The collection can be filtered via query parameters similar to how work packages are filtered. In addition to the provided filter, the result set is always limited to only contain projects the client is allowed to see.
Prior to OpenProject 17.0, only projects existed and the concept of workspaces wasn't implemented in the API. With 17.0 the other workspace types (program and portfolio) exist and will be returned alongside projects by this endpoint. This might surprise typed clients.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.project_collection_model import ProjectCollectionModel
from auto_slopp.openproject.openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://openproject.melvin.beer
# See configuration.py for a list of all supported configuration parameters.
configuration = auto_slopp.openproject.openapi_client.Configuration(
    host = "https://openproject.melvin.beer"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure HTTP basic authorization: BasicAuth
configuration = auto_slopp.openproject.openapi_client.Configuration(
    username = os.environ["USERNAME"],
    password = os.environ["PASSWORD"]
)

# Enter a context with an instance of the API client
with auto_slopp.openproject.openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = auto_slopp.openproject.openapi_client.ProjectsApi(api_client)
    filters = '[{ \"ancestor\": { \"operator\": \"=\", \"values\": [\"1\"] }\" }]' # str | JSON specifying filter conditions. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported filters are:  + active: based on the active property of the project + ancestor: filters projects by their ancestor. A project is not considered to be its own ancestor. + available_project_attributes: filters projects based on the activated project project attributes. + created_at: based on the time the project was created + favorited: based on the favorited property of the project + id: based on projects' id. + latest_activity_at: based on the time the last activity was registered on a project. + name_and_identifier: based on both the name and the identifier. + parent_id: filters projects by their parent. + principal: based on members of the project. + project_phase_any: based on the project phases active in a project. + project_status_code: based on status code of the project + storage_id: filters projects by linked storages + storage_url: filters projects by linked storages identified by the host url + type_id: based on the types active in a project. + user_action: based on the actions the current user has in the project. + visible: based on the visibility for the user (id) provided as the filter value. This filter is useful for admins to identify the projects visible to a user.  There might also be additional filters based on the custom fields that have been configured.  Each defined lifecycle step will also define a filter in this list endpoint. Given that the elements are not static but rather dynamically created on each OpenProject instance, a list cannot be provided. Those filters follow the schema: + project_start_gate_[id]: a filter on a project phase's start gate active in a project. The id is the id of the phase the gate belongs to. + project_finish_gate_[id]: a filter on a project phase's finish gate active in a project. The id is the id of the phase the gate belongs to. + project_phase_[id]: a filter on a project phase active in a project. The id is the id of the phase queried for. (optional)
    sort_by = '[[\"id\", \"asc\"]]' # str | JSON specifying sort criteria. Currently supported orders are:  + id + name + typeahead (sorting by hierarchy and name) + created_at + public + latest_activity_at + required_disk_space  There might also be additional orders based on the custom fields that have been configured. (optional)
    select = 'total,elements/identifier,elements/name' # str | Comma separated list of properties to include. (optional)

    try:
        # List projects
        api_response = api_instance.list_projects(filters=filters, sort_by=sort_by, select=select)
        print("The response of ProjectsApi->list_projects:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProjectsApi->list_projects: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **filters** | **str**| JSON specifying filter conditions. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported filters are:  + active: based on the active property of the project + ancestor: filters projects by their ancestor. A project is not considered to be its own ancestor. + available_project_attributes: filters projects based on the activated project project attributes. + created_at: based on the time the project was created + favorited: based on the favorited property of the project + id: based on projects&#39; id. + latest_activity_at: based on the time the last activity was registered on a project. + name_and_identifier: based on both the name and the identifier. + parent_id: filters projects by their parent. + principal: based on members of the project. + project_phase_any: based on the project phases active in a project. + project_status_code: based on status code of the project + storage_id: filters projects by linked storages + storage_url: filters projects by linked storages identified by the host url + type_id: based on the types active in a project. + user_action: based on the actions the current user has in the project. + visible: based on the visibility for the user (id) provided as the filter value. This filter is useful for admins to identify the projects visible to a user.  There might also be additional filters based on the custom fields that have been configured.  Each defined lifecycle step will also define a filter in this list endpoint. Given that the elements are not static but rather dynamically created on each OpenProject instance, a list cannot be provided. Those filters follow the schema: + project_start_gate_[id]: a filter on a project phase&#39;s start gate active in a project. The id is the id of the phase the gate belongs to. + project_finish_gate_[id]: a filter on a project phase&#39;s finish gate active in a project. The id is the id of the phase the gate belongs to. + project_phase_[id]: a filter on a project phase active in a project. The id is the id of the phase queried for. | [optional] 
 **sort_by** | **str**| JSON specifying sort criteria. Currently supported orders are:  + id + name + typeahead (sorting by hierarchy and name) + created_at + public + latest_activity_at + required_disk_space  There might also be additional orders based on the custom fields that have been configured. | [optional] 
 **select** | **str**| Comma separated list of properties to include. | [optional] 

### Return type

[**ProjectCollectionModel**](ProjectCollectionModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**400** | Returned if the client sends invalid request parameters e.g. filters |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_projects_with_version**
> object list_projects_with_version(id)

List projects having version

This endpoint lists the projects where the given version is available.

The projects returned depend on the sharing settings of the given version,
but are also limited to the projects that the current user is allowed to see.

This endpoint is deprecated and replaced by [`/api/v3/versions/{id}/workspaces`](https://www.openproject.org/docs/api/endpoints/projects/#list-workspaces-having-version)

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://openproject.melvin.beer
# See configuration.py for a list of all supported configuration parameters.
configuration = auto_slopp.openproject.openapi_client.Configuration(
    host = "https://openproject.melvin.beer"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure HTTP basic authorization: BasicAuth
configuration = auto_slopp.openproject.openapi_client.Configuration(
    username = os.environ["USERNAME"],
    password = os.environ["PASSWORD"]
)

# Enter a context with an instance of the API client
with auto_slopp.openproject.openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = auto_slopp.openproject.openapi_client.ProjectsApi(api_client)
    id = 1 # int | Version id

    try:
        # List projects having version
        api_response = api_instance.list_projects_with_version(id)
        print("The response of ProjectsApi->list_projects_with_version:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProjectsApi->list_projects_with_version: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Version id | 

### Return type

**object**

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**404** | Returned if the version does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view work packages **or** manage versions (any project where the given version is available)  *Note: A client without sufficient permissions shall not be able to test for the existence of a version. That&#39;s why a 404 is returned here, even if a 403 might be more appropriate.* |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_workspaces_with_version**
> object list_workspaces_with_version(id)

List workspaces having version

This endpoint lists the workspaces where the given version is available.

The workspaces returned depend on the sharing settings of the given version,
but are also limited to the workspaces that the current user is allowed to see.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://openproject.melvin.beer
# See configuration.py for a list of all supported configuration parameters.
configuration = auto_slopp.openproject.openapi_client.Configuration(
    host = "https://openproject.melvin.beer"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure HTTP basic authorization: BasicAuth
configuration = auto_slopp.openproject.openapi_client.Configuration(
    username = os.environ["USERNAME"],
    password = os.environ["PASSWORD"]
)

# Enter a context with an instance of the API client
with auto_slopp.openproject.openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = auto_slopp.openproject.openapi_client.ProjectsApi(api_client)
    id = 1 # int | Version id

    try:
        # List workspaces having version
        api_response = api_instance.list_workspaces_with_version(id)
        print("The response of ProjectsApi->list_workspaces_with_version:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProjectsApi->list_workspaces_with_version: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Version id | 

### Return type

**object**

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**404** | Returned if the version does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view work packages **or** manage versions (any workspace where the given version is available)  *Note: A client without sufficient permissions shall not be able to test for the existence of a version. That&#39;s why a 404 is returned here, even if a 403 might be more appropriate.* |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **project_copy_form**
> project_copy_form(id)

Project copy form



### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://openproject.melvin.beer
# See configuration.py for a list of all supported configuration parameters.
configuration = auto_slopp.openproject.openapi_client.Configuration(
    host = "https://openproject.melvin.beer"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure HTTP basic authorization: BasicAuth
configuration = auto_slopp.openproject.openapi_client.Configuration(
    username = os.environ["USERNAME"],
    password = os.environ["PASSWORD"]
)

# Enter a context with an instance of the API client
with auto_slopp.openproject.openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = auto_slopp.openproject.openapi_client.ProjectsApi(api_client)
    id = 1 # int | Project id

    try:
        # Project copy form
        api_instance.project_copy_form(id)
    except Exception as e:
        print("Exception when calling ProjectsApi->project_copy_form: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Project id | 

### Return type

void (empty response body)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json, text/plain

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**400** | Occurs when the client did not send a valid JSON object in the request body. |  -  |
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** copy projects in the source project |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **project_create_form**
> object project_create_form(body=body)

Project create form



### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://openproject.melvin.beer
# See configuration.py for a list of all supported configuration parameters.
configuration = auto_slopp.openproject.openapi_client.Configuration(
    host = "https://openproject.melvin.beer"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure HTTP basic authorization: BasicAuth
configuration = auto_slopp.openproject.openapi_client.Configuration(
    username = os.environ["USERNAME"],
    password = os.environ["PASSWORD"]
)

# Enter a context with an instance of the API client
with auto_slopp.openproject.openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = auto_slopp.openproject.openapi_client.ProjectsApi(api_client)
    body = None # object |  (optional)

    try:
        # Project create form
        api_response = api_instance.project_create_form(body=body)
        print("The response of ProjectsApi->project_create_form:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProjectsApi->project_create_form: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **object**|  | [optional] 

### Return type

**object**

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/hal+json, text/plain

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**400** | Occurs when the client did not send a valid JSON object in the request body. |  -  |
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** add project which is a global permission |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **project_update_form**
> project_update_form(id, body=body)

Project update form



### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://openproject.melvin.beer
# See configuration.py for a list of all supported configuration parameters.
configuration = auto_slopp.openproject.openapi_client.Configuration(
    host = "https://openproject.melvin.beer"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure HTTP basic authorization: BasicAuth
configuration = auto_slopp.openproject.openapi_client.Configuration(
    username = os.environ["USERNAME"],
    password = os.environ["PASSWORD"]
)

# Enter a context with an instance of the API client
with auto_slopp.openproject.openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = auto_slopp.openproject.openapi_client.ProjectsApi(api_client)
    id = 1 # int | Project id
    body = None # object |  (optional)

    try:
        # Project update form
        api_instance.project_update_form(id, body=body)
    except Exception as e:
        print("Exception when calling ProjectsApi->project_update_form: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Project id | 
 **body** | **object**|  | [optional] 

### Return type

void (empty response body)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/hal+json, text/plain

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**400** | Occurs when the client did not send a valid JSON object in the request body. |  -  |
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** edit projects in the project |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **unfavorite_project**
> unfavorite_project(id)

Unfavorite Project

Removes the project from the current user's favorites.

This endpoint is deprecated and replaced by [`/api/v3/workspaces/{id}/favorite`](https://www.openproject.org/docs/api/endpoints/workspaces/#unfavorite-workspace)

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://openproject.melvin.beer
# See configuration.py for a list of all supported configuration parameters.
configuration = auto_slopp.openproject.openapi_client.Configuration(
    host = "https://openproject.melvin.beer"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure HTTP basic authorization: BasicAuth
configuration = auto_slopp.openproject.openapi_client.Configuration(
    username = os.environ["USERNAME"],
    password = os.environ["PASSWORD"]
)

# Enter a context with an instance of the API client
with auto_slopp.openproject.openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = auto_slopp.openproject.openapi_client.ProjectsApi(api_client)
    id = 1 # int | Project id

    try:
        # Unfavorite Project
        api_instance.unfavorite_project(id)
    except Exception as e:
        print("Exception when calling ProjectsApi->unfavorite_project: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Project id | 

### Return type

void (empty response body)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | Returned if the project was successfully removed from favorites. |  -  |
**404** | Returned if the project does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view project |  -  |
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** logged in |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_project**
> ProjectModel update_project(id, project_model=project_model)

Update Project

Updates the given project by applying the attributes provided in the body.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.project_model import ProjectModel
from auto_slopp.openproject.openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://openproject.melvin.beer
# See configuration.py for a list of all supported configuration parameters.
configuration = auto_slopp.openproject.openapi_client.Configuration(
    host = "https://openproject.melvin.beer"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure HTTP basic authorization: BasicAuth
configuration = auto_slopp.openproject.openapi_client.Configuration(
    username = os.environ["USERNAME"],
    password = os.environ["PASSWORD"]
)

# Enter a context with an instance of the API client
with auto_slopp.openproject.openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = auto_slopp.openproject.openapi_client.ProjectsApi(api_client)
    id = 1 # int | Project id
    project_model = auto_slopp.openproject.openapi_client.ProjectModel() # ProjectModel |  (optional)

    try:
        # Update Project
        api_response = api_instance.update_project(id, project_model=project_model)
        print("The response of ProjectsApi->update_project:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProjectsApi->update_project: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Project id | 
 **project_model** | [**ProjectModel**](ProjectModel.md)|  | [optional] 

### Return type

[**ProjectModel**](ProjectModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/hal+json, text/plain

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**400** | Occurs when the client did not send a valid JSON object in the request body. |  -  |
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** edit project for the project to be altered |  -  |
**404** | Returned if the project does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view project  *Note: A client without sufficient permissions shall not be able to test for the existence of a version. That&#39;s why a 404 is returned here, even if a 403 might be more appropriate.* |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |
**422** | Returned if:  * a constraint for a property was violated (&#x60;PropertyConstraintViolation&#x60;) |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **view_project**
> ProjectModel view_project(id)

View project



### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.project_model import ProjectModel
from auto_slopp.openproject.openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://openproject.melvin.beer
# See configuration.py for a list of all supported configuration parameters.
configuration = auto_slopp.openproject.openapi_client.Configuration(
    host = "https://openproject.melvin.beer"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure HTTP basic authorization: BasicAuth
configuration = auto_slopp.openproject.openapi_client.Configuration(
    username = os.environ["USERNAME"],
    password = os.environ["PASSWORD"]
)

# Enter a context with an instance of the API client
with auto_slopp.openproject.openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = auto_slopp.openproject.openapi_client.ProjectsApi(api_client)
    id = 1 # int | Project id

    try:
        # View project
        api_response = api_instance.view_project(id)
        print("The response of ProjectsApi->view_project:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProjectsApi->view_project: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Project id | 

### Return type

[**ProjectModel**](ProjectModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**404** | Returned if the project does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view project  *Note: A client without sufficient permissions shall not be able to test for the existence of a project. That&#39;s why a 404 is returned here, even if a 403 might be more appropriate.* |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **view_project_configuration**
> ProjectConfigurationModel view_project_configuration(id)

View project configuration

Returns the configuration scoped to a specific project, including all global
configuration properties plus project-specific settings.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.project_configuration_model import ProjectConfigurationModel
from auto_slopp.openproject.openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://openproject.melvin.beer
# See configuration.py for a list of all supported configuration parameters.
configuration = auto_slopp.openproject.openapi_client.Configuration(
    host = "https://openproject.melvin.beer"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure HTTP basic authorization: BasicAuth
configuration = auto_slopp.openproject.openapi_client.Configuration(
    username = os.environ["USERNAME"],
    password = os.environ["PASSWORD"]
)

# Enter a context with an instance of the API client
with auto_slopp.openproject.openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = auto_slopp.openproject.openapi_client.ProjectsApi(api_client)
    id = 1 # int | Project id

    try:
        # View project configuration
        api_response = api_instance.view_project_configuration(id)
        print("The response of ProjectsApi->view_project_configuration:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProjectsApi->view_project_configuration: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Project id | 

### Return type

[**ProjectConfigurationModel**](ProjectConfigurationModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**404** | Returned if the project does not exist or the user cannot view it. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **view_project_schema**
> WorkspacesSchemaModel view_project_schema()

View project schema

Provides the schema describing a project resource.
This endpoint is deprecated. As projects are workspaces, an equivalent schema can be found fetching `/api/v3/workspaces/schema`.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.workspaces_schema_model import WorkspacesSchemaModel
from auto_slopp.openproject.openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://openproject.melvin.beer
# See configuration.py for a list of all supported configuration parameters.
configuration = auto_slopp.openproject.openapi_client.Configuration(
    host = "https://openproject.melvin.beer"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure HTTP basic authorization: BasicAuth
configuration = auto_slopp.openproject.openapi_client.Configuration(
    username = os.environ["USERNAME"],
    password = os.environ["PASSWORD"]
)

# Enter a context with an instance of the API client
with auto_slopp.openproject.openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = auto_slopp.openproject.openapi_client.ProjectsApi(api_client)

    try:
        # View project schema
        api_response = api_instance.view_project_schema()
        print("The response of ProjectsApi->view_project_schema:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProjectsApi->view_project_schema: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**WorkspacesSchemaModel**](WorkspacesSchemaModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **view_project_status**
> object view_project_status(id)

View project status



### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://openproject.melvin.beer
# See configuration.py for a list of all supported configuration parameters.
configuration = auto_slopp.openproject.openapi_client.Configuration(
    host = "https://openproject.melvin.beer"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure HTTP basic authorization: BasicAuth
configuration = auto_slopp.openproject.openapi_client.Configuration(
    username = os.environ["USERNAME"],
    password = os.environ["PASSWORD"]
)

# Enter a context with an instance of the API client
with auto_slopp.openproject.openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = auto_slopp.openproject.openapi_client.ProjectsApi(api_client)
    id = 'on_track' # str | Project status id

    try:
        # View project status
        api_response = api_instance.view_project_status(id)
        print("The response of ProjectsApi->view_project_status:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProjectsApi->view_project_status: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| Project status id | 

### Return type

**object**

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**404** | Returned if the project status does not exist. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

