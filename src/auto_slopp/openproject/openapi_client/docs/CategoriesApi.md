# auto_slopp.openproject.openapi_client.CategoriesApi

All URIs are relative to *https://openproject.melvin.beer*

Method | HTTP request | Description
------------- | ------------- | -------------
[**list_categories_of_a_project**](CategoriesApi.md#list_categories_of_a_project) | **GET** /api/v3/projects/{id}/categories | List categories of a project
[**list_categories_of_a_workspace**](CategoriesApi.md#list_categories_of_a_workspace) | **GET** /api/v3/workspaces/{id}/categories | List categories of a workspace
[**view_category**](CategoriesApi.md#view_category) | **GET** /api/v3/categories/{id} | View Category


# **list_categories_of_a_project**
> CategoriesByWorkspaceModel list_categories_of_a_project(id)

List categories of a project

List all categories of a project
This endpoint is deprecated and replaced by [`/api/v3/workspaces/{id}/categories`](https://www.openproject.org/docs/api/endpoints/categories/#list-categories-of-a-workspace) 

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.categories_by_workspace_model import CategoriesByWorkspaceModel
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
    api_instance = auto_slopp.openproject.openapi_client.CategoriesApi(api_client)
    id = 1 # int | ID of the project whose categories will be listed

    try:
        # List categories of a project
        api_response = api_instance.list_categories_of_a_project(id)
        print("The response of CategoriesApi->list_categories_of_a_project:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CategoriesApi->list_categories_of_a_project: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| ID of the project whose categories will be listed | 

### Return type

[**CategoriesByWorkspaceModel**](CategoriesByWorkspaceModel.md)

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

# **list_categories_of_a_workspace**
> CategoriesByWorkspaceModel list_categories_of_a_workspace(id)

List categories of a workspace

List all categories of a project

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.categories_by_workspace_model import CategoriesByWorkspaceModel
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
    api_instance = auto_slopp.openproject.openapi_client.CategoriesApi(api_client)
    id = 1 # int | ID of the workspace whose categories will be listed

    try:
        # List categories of a workspace
        api_response = api_instance.list_categories_of_a_workspace(id)
        print("The response of CategoriesApi->list_categories_of_a_workspace:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CategoriesApi->list_categories_of_a_workspace: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| ID of the workspace whose categories will be listed | 

### Return type

[**CategoriesByWorkspaceModel**](CategoriesByWorkspaceModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**404** | Returned if the workspace does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view workspace  *Note: A client without sufficient permissions shall not be able to test for the existence of a workspace. That&#39;s why a 404 is returned here, even if a 403 might be more appropriate.* |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **view_category**
> CategoryModel view_category(id)

View Category



### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.category_model import CategoryModel
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
    api_instance = auto_slopp.openproject.openapi_client.CategoriesApi(api_client)
    id = 1 # int | Category id

    try:
        # View Category
        api_response = api_instance.view_category(id)
        print("The response of CategoriesApi->view_category:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CategoriesApi->view_category: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Category id | 

### Return type

[**CategoryModel**](CategoryModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**404** | Returned if the category does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view project (defining the category)  *Note: A client without sufficient permissions shall not be able to test for the existence of a category. That&#39;s why a 404 is returned here, even if a 403 might be more appropriate.* |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

