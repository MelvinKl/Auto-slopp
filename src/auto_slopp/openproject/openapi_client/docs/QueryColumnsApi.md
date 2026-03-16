# auto_slopp.openproject.openapi_client.QueryColumnsApi

All URIs are relative to *https://openproject.melvin.beer*

Method | HTTP request | Description
------------- | ------------- | -------------
[**view_query_column**](QueryColumnsApi.md#view_query_column) | **GET** /api/v3/queries/columns/{id} | View Query Column


# **view_query_column**
> QueryColumnModel view_query_column(id)

View Query Column

Retrieve an individual QueryColumn as identified by the `id` parameter.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.query_column_model import QueryColumnModel
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
    api_instance = auto_slopp.openproject.openapi_client.QueryColumnsApi(api_client)
    id = 'priority' # str | QueryColumn id

    try:
        # View Query Column
        api_response = api_instance.view_query_column(id)
        print("The response of QueryColumnsApi->view_query_column:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling QueryColumnsApi->view_query_column: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| QueryColumn id | 

### Return type

[**QueryColumnModel**](QueryColumnModel.md)

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
**404** | Returned if the QueryColumn does not exist. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

