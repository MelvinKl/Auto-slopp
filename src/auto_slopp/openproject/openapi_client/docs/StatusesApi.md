# auto_slopp.openproject.openapi_client.StatusesApi

All URIs are relative to *https://openproject.melvin.beer*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_status**](StatusesApi.md#get_status) | **GET** /api/v3/statuses/{id} | Get a work package status
[**list_statuses**](StatusesApi.md#list_statuses) | **GET** /api/v3/statuses | List the collection of all statuses


# **get_status**
> StatusModel get_status(id)

Get a work package status

Returns a work package status by its unique identifier.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.status_model import StatusModel
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
    api_instance = auto_slopp.openproject.openapi_client.StatusesApi(api_client)
    id = 1 # int | Status id

    try:
        # Get a work package status
        api_response = api_instance.get_status(id)
        print("The response of StatusesApi->get_status:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling StatusesApi->get_status: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Status id | 

### Return type

[**StatusModel**](StatusModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** view work package (on any project) |  -  |
**404** | Returned if the status does not exist. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_statuses**
> StatusCollectionModel list_statuses()

List the collection of all statuses

Returns a collection of all work package statuses.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.status_collection_model import StatusCollectionModel
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
    api_instance = auto_slopp.openproject.openapi_client.StatusesApi(api_client)

    try:
        # List the collection of all statuses
        api_response = api_instance.list_statuses()
        print("The response of StatusesApi->list_statuses:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling StatusesApi->list_statuses: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**StatusCollectionModel**](StatusCollectionModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** view work package (on any project) |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

