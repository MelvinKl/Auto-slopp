# auto_slopp.openproject.openapi_client.TypesApi

All URIs are relative to *https://openproject.melvin.beer*

Method | HTTP request | Description
------------- | ------------- | -------------
[**list_all_types**](TypesApi.md#list_all_types) | **GET** /api/v3/types | List all Types
[**list_types_available_in_a_project**](TypesApi.md#list_types_available_in_a_project) | **GET** /api/v3/projects/{id}/types | List types available in a project
[**list_types_available_in_a_workspace**](TypesApi.md#list_types_available_in_a_workspace) | **GET** /api/v3/workspaces/{id}/types | List types available in a workspace
[**view_type**](TypesApi.md#view_type) | **GET** /api/v3/types/{id} | View Type


# **list_all_types**
> object list_all_types()

List all Types



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
    api_instance = auto_slopp.openproject.openapi_client.TypesApi(api_client)

    try:
        # List all Types
        api_response = api_instance.list_all_types()
        print("The response of TypesApi->list_all_types:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TypesApi->list_all_types: %s\n" % e)
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
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** view work package or manage types (on any project) |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_types_available_in_a_project**
> TypesByWorkspaceModel list_types_available_in_a_project(id)

List types available in a project

This endpoint lists the types that are *available* in a given project.
This endpoint is deprecated and replaced by [`/api/v3/workspaces/{id}/types`](https://www.openproject.org/docs/api/endpoints/types/#list-types-available-in-a-workspace)

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
    api_instance = auto_slopp.openproject.openapi_client.TypesApi(api_client)
    id = 1 # int | ID of the project whose types will be listed

    try:
        # List types available in a project
        api_response = api_instance.list_types_available_in_a_project(id)
        print("The response of TypesApi->list_types_available_in_a_project:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TypesApi->list_types_available_in_a_project: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| ID of the project whose types will be listed | 

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
**404** | Returned if the project does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view work packages **or** manage types (on given project)  *Note: A client without sufficient permissions shall not be able to test for the existence of a project. That&#39;s why a 404 is returned here, even if a 403 might be more appropriate.* |  -  |

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
    api_instance = auto_slopp.openproject.openapi_client.TypesApi(api_client)
    id = 1 # int | ID of the workspace whose types will be listed

    try:
        # List types available in a workspace
        api_response = api_instance.list_types_available_in_a_workspace(id)
        print("The response of TypesApi->list_types_available_in_a_workspace:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TypesApi->list_types_available_in_a_workspace: %s\n" % e)
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

# **view_type**
> TypeModel view_type(id)

View Type



### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.type_model import TypeModel
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
    api_instance = auto_slopp.openproject.openapi_client.TypesApi(api_client)
    id = 1 # int | Type id

    try:
        # View Type
        api_response = api_instance.view_type(id)
        print("The response of TypesApi->view_type:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TypesApi->view_type: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Type id | 

### Return type

[**TypeModel**](TypeModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** view work package or manage types (on any project) |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

