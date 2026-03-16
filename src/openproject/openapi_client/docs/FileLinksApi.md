# openproject_client.FileLinksApi

All URIs are relative to *https://openproject.melvin.beer*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_project_storage**](FileLinksApi.md#get_project_storage) | **GET** /api/v3/project_storages/{id} | Gets a project storage
[**list_project_storages**](FileLinksApi.md#list_project_storages) | **GET** /api/v3/project_storages | Gets a list of project storages
[**open_project_storage**](FileLinksApi.md#open_project_storage) | **GET** /api/v3/project_storages/{id}/open | Open the project storage
[**open_storage**](FileLinksApi.md#open_storage) | **GET** /api/v3/storages/{id}/open | Open the storage


# **get_project_storage**
> ProjectStorageModel get_project_storage(id)

Gets a project storage

Gets a project storage resource. This resource contains all data that is applicable on the relation between a
storage and a project.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.project_storage_model import ProjectStorageModel
from openproject_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://openproject.melvin.beer
# See configuration.py for a list of all supported configuration parameters.
configuration = openproject_client.Configuration(
    host = "https://openproject.melvin.beer"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure HTTP basic authorization: BasicAuth
configuration = openproject_client.Configuration(
    username = os.environ["USERNAME"],
    password = os.environ["PASSWORD"]
)

# Enter a context with an instance of the API client
with openproject_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openproject_client.FileLinksApi(api_client)
    id = 1337 # int | Project storage id

    try:
        # Gets a project storage
        api_response = api_instance.get_project_storage(id)
        print("The response of FileLinksApi->get_project_storage:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FileLinksApi->get_project_storage: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Project storage id | 

### Return type

[**ProjectStorageModel**](ProjectStorageModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**404** | Returned if the project storage does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view file links |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_project_storages**
> ProjectStorageCollectionModel list_project_storages(filters=filters)

Gets a list of project storages

Gets a collection of all project storages that meet the provided filters and the user has permission to see them.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.project_storage_collection_model import ProjectStorageCollectionModel
from openproject_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://openproject.melvin.beer
# See configuration.py for a list of all supported configuration parameters.
configuration = openproject_client.Configuration(
    host = "https://openproject.melvin.beer"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure HTTP basic authorization: BasicAuth
configuration = openproject_client.Configuration(
    username = os.environ["USERNAME"],
    password = os.environ["PASSWORD"]
)

# Enter a context with an instance of the API client
with openproject_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openproject_client.FileLinksApi(api_client)
    filters = '[]' # str | JSON specifying filter conditions. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported filters are:  - project_id - storage_id - storage_url (optional) (default to '[]')

    try:
        # Gets a list of project storages
        api_response = api_instance.list_project_storages(filters=filters)
        print("The response of FileLinksApi->list_project_storages:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FileLinksApi->list_project_storages: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **filters** | **str**| JSON specifying filter conditions. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported filters are:  - project_id - storage_id - storage_url | [optional] [default to &#39;[]&#39;]

### Return type

[**ProjectStorageCollectionModel**](ProjectStorageCollectionModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**400** | Returned if any given filter is invalid. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **open_project_storage**
> open_project_storage(id)

Open the project storage

Gets a redirect to the location of the project storage's remote origin. If the project storage has a project
folder, it is opened at this location. If not, the storage root is opened.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://openproject.melvin.beer
# See configuration.py for a list of all supported configuration parameters.
configuration = openproject_client.Configuration(
    host = "https://openproject.melvin.beer"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure HTTP basic authorization: BasicAuth
configuration = openproject_client.Configuration(
    username = os.environ["USERNAME"],
    password = os.environ["PASSWORD"]
)

# Enter a context with an instance of the API client
with openproject_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openproject_client.FileLinksApi(api_client)
    id = 1337 # int | Project storage id

    try:
        # Open the project storage
        api_instance.open_project_storage(id)
    except Exception as e:
        print("Exception when calling FileLinksApi->open_project_storage: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Project storage id | 

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
**303** | Redirect |  * Location -  <br>  |
**403** | Returned if the authorization token of the current user grants no permission to access the remote storage. |  -  |
**404** | Returned if the project storage does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view file links |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **open_storage**
> open_storage(id)

Open the storage

Gets a redirect to the location of the storage's remote origin. The storage's files root should be the target
location.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://openproject.melvin.beer
# See configuration.py for a list of all supported configuration parameters.
configuration = openproject_client.Configuration(
    host = "https://openproject.melvin.beer"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure HTTP basic authorization: BasicAuth
configuration = openproject_client.Configuration(
    username = os.environ["USERNAME"],
    password = os.environ["PASSWORD"]
)

# Enter a context with an instance of the API client
with openproject_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openproject_client.FileLinksApi(api_client)
    id = 1337 # int | Storage id

    try:
        # Open the storage
        api_instance.open_storage(id)
    except Exception as e:
        print("Exception when calling FileLinksApi->open_storage: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Storage id | 

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
**303** | Redirect |  * Location -  <br>  |
**404** | Returned if the storage does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view file links |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

