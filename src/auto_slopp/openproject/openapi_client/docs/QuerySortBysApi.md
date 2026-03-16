# auto_slopp.openproject.openapi_client.QuerySortBysApi

All URIs are relative to *https://openproject.melvin.beer*

Method | HTTP request | Description
------------- | ------------- | -------------
[**view_query_sort_by**](QuerySortBysApi.md#view_query_sort_by) | **GET** /api/v3/queries/sort_bys/{id} | View Query Sort By


# **view_query_sort_by**
> QuerySortByModel view_query_sort_by(id)

View Query Sort By

Retrieve an individual QuerySortBy as identified by the id parameter.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.query_sort_by_model import QuerySortByModel
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
    api_instance = auto_slopp.openproject.openapi_client.QuerySortBysApi(api_client)
    id = 'status-asc' # str | QuerySortBy identifier. The identifier is a combination of the column identifier and the direction.

    try:
        # View Query Sort By
        api_response = api_instance.view_query_sort_by(id)
        print("The response of QuerySortBysApi->view_query_sort_by:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling QuerySortBysApi->view_query_sort_by: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| QuerySortBy identifier. The identifier is a combination of the column identifier and the direction. | 

### Return type

[**QuerySortByModel**](QuerySortByModel.md)

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
**404** | Returned if the QuerySortBy does not exist. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

