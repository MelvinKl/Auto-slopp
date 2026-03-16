# openproject_client.QueryFiltersApi

All URIs are relative to *https://openproject.melvin.beer*

Method | HTTP request | Description
------------- | ------------- | -------------
[**view_query_filter**](QueryFiltersApi.md#view_query_filter) | **GET** /api/v3/queries/filters/{id} | View Query Filter


# **view_query_filter**
> QueryFilterModel view_query_filter(id)

View Query Filter

Retrieve an individual QueryFilter as identified by the id parameter.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.query_filter_model import QueryFilterModel
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
    api_instance = openproject_client.QueryFiltersApi(api_client)
    id = 'status' # str | QueryFilter identifier

    try:
        # View Query Filter
        api_response = api_instance.view_query_filter(id)
        print("The response of QueryFiltersApi->view_query_filter:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling QueryFiltersApi->view_query_filter: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| QueryFilter identifier | 

### Return type

[**QueryFilterModel**](QueryFilterModel.md)

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
**404** | Returned if the QueryFilter does not exist. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

