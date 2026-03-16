# auto_slopp.openproject.openapi_client.VersionsApi

All URIs are relative to *https://openproject.melvin.beer*

Method | HTTP request | Description
------------- | ------------- | -------------
[**available_projects_for_versions**](VersionsApi.md#available_projects_for_versions) | **GET** /api/v3/versions/available_projects | Available projects for versions
[**create_version**](VersionsApi.md#create_version) | **POST** /api/v3/versions | Create version
[**delete_version**](VersionsApi.md#delete_version) | **DELETE** /api/v3/versions/{id} | Delete version
[**get_version**](VersionsApi.md#get_version) | **GET** /api/v3/versions/{id} | Get version
[**list_versions**](VersionsApi.md#list_versions) | **GET** /api/v3/versions | List versions
[**list_versions_available_in_a_project**](VersionsApi.md#list_versions_available_in_a_project) | **GET** /api/v3/projects/{id}/versions | List versions available in a project
[**list_versions_available_in_a_workspace**](VersionsApi.md#list_versions_available_in_a_workspace) | **GET** /api/v3/workspaces/{id}/versions | List versions available in a workspace
[**update_version**](VersionsApi.md#update_version) | **PATCH** /api/v3/versions/{id} | Update Version
[**version_create_form**](VersionsApi.md#version_create_form) | **POST** /api/v3/versions/form | Version create form
[**version_update_form**](VersionsApi.md#version_update_form) | **POST** /api/v3/versions/{id}/form | Version update form
[**view_version_schema**](VersionsApi.md#view_version_schema) | **GET** /api/v3/versions/schema | View version schema


# **available_projects_for_versions**
> object available_projects_for_versions()

Available projects for versions

Gets a list of projects in which a version can be created in. The list contains all projects in which the user issuing the request has the manage versions permissions.

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
    api_instance = auto_slopp.openproject.openapi_client.VersionsApi(api_client)

    try:
        # Available projects for versions
        api_response = api_instance.available_projects_for_versions()
        print("The response of VersionsApi->available_projects_for_versions:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling VersionsApi->available_projects_for_versions: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

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
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** manage versions |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_version**
> VersionReadModel create_version(version_write_model=version_write_model)

Create version

Creates a new version applying the attributes provided in the body. Please note that while there is a fixed set
of attributes, custom fields can extend a version's attributes and are accepted by the endpoint.

You can use the form and schema to be retrieve the valid attribute values and by that be guided towards
successful creation.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.version_read_model import VersionReadModel
from auto_slopp.openproject.openapi_client.models.version_write_model import VersionWriteModel
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
    api_instance = auto_slopp.openproject.openapi_client.VersionsApi(api_client)
    version_write_model = auto_slopp.openproject.openapi_client.VersionWriteModel() # VersionWriteModel |  (optional)

    try:
        # Create version
        api_response = api_instance.create_version(version_write_model=version_write_model)
        print("The response of VersionsApi->create_version:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling VersionsApi->create_version: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **version_write_model** | [**VersionWriteModel**](VersionWriteModel.md)|  | [optional] 

### Return type

[**VersionReadModel**](VersionReadModel.md)

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
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** Manage versions |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |
**422** | Returned if:  * a constraint for a property was violated (&#x60;PropertyConstraintViolation&#x60;) |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_version**
> delete_version(id)

Delete version

Deletes the version. Entities associated to the version will no longer be assigned to it.

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
    api_instance = auto_slopp.openproject.openapi_client.VersionsApi(api_client)
    id = 1 # int | Version id

    try:
        # Delete version
        api_instance.delete_version(id)
    except Exception as e:
        print("Exception when calling VersionsApi->delete_version: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Version id | 

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
**204** | Returned if the version was successfully deleted |  -  |
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** manage versions |  -  |
**404** | Returned if the version does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view work packages **or** manage versions (any project where the version is available)  *Note: A client without sufficient permissions shall not be able to test for the existence of a version. That&#39;s why a 404 is returned here, even if a 403 might be more appropriate.* |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_version**
> VersionReadModel get_version(id)

Get version

Retrieves a version defined by its unique identifier.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.version_read_model import VersionReadModel
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
    api_instance = auto_slopp.openproject.openapi_client.VersionsApi(api_client)
    id = 1 # int | Version id

    try:
        # Get version
        api_response = api_instance.get_version(id)
        print("The response of VersionsApi->get_version:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling VersionsApi->get_version: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Version id | 

### Return type

[**VersionReadModel**](VersionReadModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**404** | Returned if the version does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view work packages **or** manage versions (any project where the version is available)  *Note: A client without sufficient permissions shall not be able to test for the existence of a version. That&#39;s why a 404 is returned here, even if a 403 might be more appropriate.* |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_versions**
> VersionCollectionModel list_versions(filters=filters, sort_by=sort_by)

List versions

Returns a collection of versions. The client can choose to filter the versions similar to how work packages are
filtered. In addition to the provided filters, the server will reduce the result set to only contain versions,
for which the requesting client has sufficient permissions (*view_work_packages*).

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.version_collection_model import VersionCollectionModel
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
    api_instance = auto_slopp.openproject.openapi_client.VersionsApi(api_client)
    filters = '[{ \"sharing\": { \"operator\": \"=\", \"values\": [\"system\"] } }]' # str | JSON specifying filter conditions. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported filters are:  - sharing: filters versions by how they are shared within the server (*none*, *descendants*, *hierarchy*, *tree*, *system*). - name: filters versions by their name. (optional)
    sort_by = '[[\"name\", \"desc\"]]' # str | JSON specifying sort criteria. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported attributes are:  - id: Sort by the version id - name: Sort by the version name using numeric collation, comparing sequences of decimal digits by their numeric value (optional)

    try:
        # List versions
        api_response = api_instance.list_versions(filters=filters, sort_by=sort_by)
        print("The response of VersionsApi->list_versions:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling VersionsApi->list_versions: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **filters** | **str**| JSON specifying filter conditions. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported filters are:  - sharing: filters versions by how they are shared within the server (*none*, *descendants*, *hierarchy*, *tree*, *system*). - name: filters versions by their name. | [optional] 
 **sort_by** | **str**| JSON specifying sort criteria. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported attributes are:  - id: Sort by the version id - name: Sort by the version name using numeric collation, comparing sequences of decimal digits by their numeric value | [optional] 

### Return type

[**VersionCollectionModel**](VersionCollectionModel.md)

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

# **list_versions_available_in_a_project**
> VersionsByWorkspaceModel list_versions_available_in_a_project(id)

List versions available in a project

This endpoint lists the versions that are *available* in a given project.
Note that due to sharing this might be more than the versions *defined* by that project.

This endpoint is deprecated and replaced by [`/api/v3/workspaces/{id}/versions`](https://www.openproject.org/docs/api/endpoints/versions/#list-versions-available-in-a-workspace)

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.versions_by_workspace_model import VersionsByWorkspaceModel
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
    api_instance = auto_slopp.openproject.openapi_client.VersionsApi(api_client)
    id = 1 # int | ID of the project whose versions will be listed

    try:
        # List versions available in a project
        api_response = api_instance.list_versions_available_in_a_project(id)
        print("The response of VersionsApi->list_versions_available_in_a_project:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling VersionsApi->list_versions_available_in_a_project: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| ID of the project whose versions will be listed | 

### Return type

[**VersionsByWorkspaceModel**](VersionsByWorkspaceModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**404** | Returned if the project does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view work packages **or** manage versions (on given project)  *Note: A client without sufficient permissions shall not be able to test for the existence of a project. That&#39;s why a 404 is returned here, even if a 403 might be more appropriate.* |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_versions_available_in_a_workspace**
> VersionsByWorkspaceModel list_versions_available_in_a_workspace(id)

List versions available in a workspace

This endpoint lists the versions that are *available* in a given workspace.
Note that due to sharing this might be more than the versions *defined* by that workspace.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.versions_by_workspace_model import VersionsByWorkspaceModel
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
    api_instance = auto_slopp.openproject.openapi_client.VersionsApi(api_client)
    id = 1 # int | ID of the workspace whose versions will be listed

    try:
        # List versions available in a workspace
        api_response = api_instance.list_versions_available_in_a_workspace(id)
        print("The response of VersionsApi->list_versions_available_in_a_workspace:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling VersionsApi->list_versions_available_in_a_workspace: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| ID of the workspace whose versions will be listed | 

### Return type

[**VersionsByWorkspaceModel**](VersionsByWorkspaceModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**404** | Returned if the workspace does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view work packages **or** manage versions (on given workspace)  *Note: A client without sufficient permissions shall not be able to test for the existence of a workspace. That&#39;s why a 404 is returned here, even if a 403 might be more appropriate.* |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_version**
> VersionReadModel update_version(id, version_write_model=version_write_model)

Update Version

Updates the given version by applying the attributes provided in the body. Please note that while there is a fixed
set of attributes, custom fields can extend a version's attributes and are accepted by the endpoint.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.version_read_model import VersionReadModel
from auto_slopp.openproject.openapi_client.models.version_write_model import VersionWriteModel
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
    api_instance = auto_slopp.openproject.openapi_client.VersionsApi(api_client)
    id = 1 # int | Version id
    version_write_model = auto_slopp.openproject.openapi_client.VersionWriteModel() # VersionWriteModel |  (optional)

    try:
        # Update Version
        api_response = api_instance.update_version(id, version_write_model=version_write_model)
        print("The response of VersionsApi->update_version:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling VersionsApi->update_version: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Version id | 
 **version_write_model** | [**VersionWriteModel**](VersionWriteModel.md)|  | [optional] 

### Return type

[**VersionReadModel**](VersionReadModel.md)

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
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** Manage versions in the version&#39;s project. |  -  |
**404** | Returned if the version does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view work packages **or** manage versions (any project where the version is available)  *Note: A client without sufficient permissions shall not be able to test for the existence of a version. That&#39;s why a 404 is returned here, even if a 403 might be more appropriate.* |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |
**422** | Returned if:  * a constraint for a property was violated (&#x60;PropertyConstraintViolation&#x60;) |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **version_create_form**
> version_create_form()

Version create form



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
    api_instance = auto_slopp.openproject.openapi_client.VersionsApi(api_client)

    try:
        # Version create form
        api_instance.version_create_form()
    except Exception as e:
        print("Exception when calling VersionsApi->version_create_form: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

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
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** manage versions in any project |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **version_update_form**
> version_update_form(id)

Version update form



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
    api_instance = auto_slopp.openproject.openapi_client.VersionsApi(api_client)
    id = 1 # int | Project id

    try:
        # Version update form
        api_instance.version_update_form(id)
    except Exception as e:
        print("Exception when calling VersionsApi->version_update_form: %s\n" % e)
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
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** manage versions in the version&#39;s project |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **view_version_schema**
> object view_version_schema()

View version schema



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
    api_instance = auto_slopp.openproject.openapi_client.VersionsApi(api_client)

    try:
        # View version schema
        api_response = api_instance.view_version_schema()
        print("The response of VersionsApi->view_version_schema:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling VersionsApi->view_version_schema: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

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
**403** | Returned if the client does not have sufficient permissions to see the schema.  **Required permission:** view work packages or manage versions on any project |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

