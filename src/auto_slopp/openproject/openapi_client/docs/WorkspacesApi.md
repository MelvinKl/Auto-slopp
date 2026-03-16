# auto_slopp.openproject.openapi_client.WorkspacesApi

All URIs are relative to *https://openproject.melvin.beer*

Method | HTTP request | Description
------------- | ------------- | -------------
[**favorite_workspace**](WorkspacesApi.md#favorite_workspace) | **POST** /api/v3/workspaces/{id}/favorite | Favorite Workspace
[**list_types_available_in_a_workspace**](WorkspacesApi.md#list_types_available_in_a_workspace) | **GET** /api/v3/workspaces/{id}/types | List types available in a workspace
[**unfavorite_workspace**](WorkspacesApi.md#unfavorite_workspace) | **DELETE** /api/v3/workspaces/{id}/favorite | Unfavorite Workspace
[**view_workspace_schema**](WorkspacesApi.md#view_workspace_schema) | **GET** /api/v3/workspaces/schema | View workspace schema


# **favorite_workspace**
> favorite_workspace(id)

Favorite Workspace

Adds the workspace to the current user's favorites.

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
    api_instance = auto_slopp.openproject.openapi_client.WorkspacesApi(api_client)
    id = 1 # int | Workspace id

    try:
        # Favorite Workspace
        api_instance.favorite_workspace(id)
    except Exception as e:
        print("Exception when calling WorkspacesApi->favorite_workspace: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Workspace id | 

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
**204** | Returned if the workspace was successfully added to favorites. |  -  |
**404** | Returned if the workspace does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view workspace |  -  |
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** logged in |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_types_available_in_a_workspace**
> TypesByWorkspaceModel list_types_available_in_a_workspace(id)

List types available in a workspace

This endpoint lists the types that are *available* in a given workspace.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.types_by_workspace_model import TypesByWorkspaceModel
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
    api_instance = auto_slopp.openproject.openapi_client.WorkspacesApi(api_client)
    id = 1 # int | ID of the workspace whose types will be listed

    try:
        # List types available in a workspace
        api_response = api_instance.list_types_available_in_a_workspace(id)
        print("The response of WorkspacesApi->list_types_available_in_a_workspace:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkspacesApi->list_types_available_in_a_workspace: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| ID of the workspace whose types will be listed | 

### Return type

[**TypesByWorkspaceModel**](TypesByWorkspaceModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**404** | Returned if the workspace does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view work packages **or** manage types (on given workspace)  *Note: A client without sufficient permissions shall not be able to test for the existence of a workspace. That&#39;s why a 404 is returned here, even if a 403 might be more appropriate.* |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **unfavorite_workspace**
> unfavorite_workspace(id)

Unfavorite Workspace

Removes the workspace from the current user's favorites.

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
    api_instance = auto_slopp.openproject.openapi_client.WorkspacesApi(api_client)
    id = 1 # int | Workspace id

    try:
        # Unfavorite Workspace
        api_instance.unfavorite_workspace(id)
    except Exception as e:
        print("Exception when calling WorkspacesApi->unfavorite_workspace: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Workspace id | 

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
**204** | Returned if the workspace was successfully removed from favorites. |  -  |
**404** | Returned if the workspace does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view workspace |  -  |
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** logged in |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **view_workspace_schema**
> WorkspacesSchemaModel view_workspace_schema()

View workspace schema



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
    api_instance = auto_slopp.openproject.openapi_client.WorkspacesApi(api_client)

    try:
        # View workspace schema
        api_response = api_instance.view_workspace_schema()
        print("The response of WorkspacesApi->view_workspace_schema:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkspacesApi->view_workspace_schema: %s\n" % e)
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

