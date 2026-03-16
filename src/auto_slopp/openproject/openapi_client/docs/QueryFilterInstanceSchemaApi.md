# auto_slopp.openproject.openapi_client.QueryFilterInstanceSchemaApi

All URIs are relative to *https://openproject.melvin.beer*

Method | HTTP request | Description
------------- | ------------- | -------------
[**list_query_filter_instance_schemas**](QueryFilterInstanceSchemaApi.md#list_query_filter_instance_schemas) | **GET** /api/v3/queries/filter_instance_schemas | List Query Filter Instance Schemas
[**list_query_filter_instance_schemas_for_project**](QueryFilterInstanceSchemaApi.md#list_query_filter_instance_schemas_for_project) | **GET** /api/v3/projects/{id}/queries/filter_instance_schemas | List Query Filter Instance Schemas for Project
[**list_query_filter_instance_schemas_for_workspace**](QueryFilterInstanceSchemaApi.md#list_query_filter_instance_schemas_for_workspace) | **GET** /api/v3/workspace/{id}/queries/filter_instance_schemas | List Query Filter Instance Schemas for Workspace
[**view_query_filter_instance_schema**](QueryFilterInstanceSchemaApi.md#view_query_filter_instance_schema) | **GET** /api/v3/queries/filter_instance_schemas/{id} | View Query Filter Instance Schema


# **list_query_filter_instance_schemas**
> object list_query_filter_instance_schemas()

List Query Filter Instance Schemas

Returns the list of QueryFilterInstanceSchemas defined for a global query. That is a query not assigned to a project.

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
    api_instance = auto_slopp.openproject.openapi_client.QueryFilterInstanceSchemaApi(api_client)

    try:
        # List Query Filter Instance Schemas
        api_response = api_instance.list_query_filter_instance_schemas()
        print("The response of QueryFilterInstanceSchemaApi->list_query_filter_instance_schemas:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling QueryFilterInstanceSchemaApi->list_query_filter_instance_schemas: %s\n" % e)
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
**403** | Returned if the client does not have sufficient permissions to see it.  **Required permission:** view work package in any project |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_query_filter_instance_schemas_for_project**
> object list_query_filter_instance_schemas_for_project(id)

List Query Filter Instance Schemas for Project

Returns the list of QueryFilterInstanceSchemas defined for a query
of the specified project.

This endpoint is deprecated and replaced by [`/api/v3/workspaces/{id}/queries/filter_instance_schemas`](https://www.openproject.org/docs/api/endpoints/query-filter-instance-schema/#list-query-filter-instance-schemas-for-workspace)

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
    api_instance = auto_slopp.openproject.openapi_client.QueryFilterInstanceSchemaApi(api_client)
    id = 1 # int | Project id

    try:
        # List Query Filter Instance Schemas for Project
        api_response = api_instance.list_query_filter_instance_schemas_for_project(id)
        print("The response of QueryFilterInstanceSchemaApi->list_query_filter_instance_schemas_for_project:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling QueryFilterInstanceSchemaApi->list_query_filter_instance_schemas_for_project: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Project id | 

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
**403** | Returned if the client does not have sufficient permissions to see it.  **Required permission:** view work package in any project |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_query_filter_instance_schemas_for_workspace**
> object list_query_filter_instance_schemas_for_workspace(id)

List Query Filter Instance Schemas for Workspace

Returns the list of QueryFilterInstanceSchemas defined for a query of the specified workspace.

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
    api_instance = auto_slopp.openproject.openapi_client.QueryFilterInstanceSchemaApi(api_client)
    id = 1 # int | Workspace id

    try:
        # List Query Filter Instance Schemas for Workspace
        api_response = api_instance.list_query_filter_instance_schemas_for_workspace(id)
        print("The response of QueryFilterInstanceSchemaApi->list_query_filter_instance_schemas_for_workspace:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling QueryFilterInstanceSchemaApi->list_query_filter_instance_schemas_for_workspace: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Workspace id | 

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
**403** | Returned if the client does not have sufficient permissions to see it.  **Required permission:** view work package in any workspace |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **view_query_filter_instance_schema**
> QueryFilterInstanceSchemaModel view_query_filter_instance_schema(id)

View Query Filter Instance Schema

Retrieve an individual QueryFilterInstanceSchema as identified by the id parameter.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.query_filter_instance_schema_model import QueryFilterInstanceSchemaModel
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
    api_instance = auto_slopp.openproject.openapi_client.QueryFilterInstanceSchemaApi(api_client)
    id = 'author' # str | QueryFilterInstanceSchema identifier. The identifier is the filter identifier.

    try:
        # View Query Filter Instance Schema
        api_response = api_instance.view_query_filter_instance_schema(id)
        print("The response of QueryFilterInstanceSchemaApi->view_query_filter_instance_schema:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling QueryFilterInstanceSchemaApi->view_query_filter_instance_schema: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| QueryFilterInstanceSchema identifier. The identifier is the filter identifier. | 

### Return type

[**QueryFilterInstanceSchemaModel**](QueryFilterInstanceSchemaModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**403** | Returned if the client does not have sufficient permissions to see it.  **Required permission:** view work package in any project |  -  |
**404** | Returned if the QueryFilterInstanceSchema does not exist. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

