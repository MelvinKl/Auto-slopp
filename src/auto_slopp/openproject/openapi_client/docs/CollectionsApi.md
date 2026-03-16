# auto_slopp.openproject.openapi_client.CollectionsApi

All URIs are relative to *https://openproject.melvin.beer*

Method | HTTP request | Description
------------- | ------------- | -------------
[**view_aggregated_result**](CollectionsApi.md#view_aggregated_result) | **GET** /api/v3/examples | view aggregated result


# **view_aggregated_result**
> view_aggregated_result(group_by=group_by, show_sums=show_sums)

view aggregated result



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
    api_instance = auto_slopp.openproject.openapi_client.CollectionsApi(api_client)
    group_by = 'status' # str | The column to group by. Note: Aggregation is as of now only supported by the work package collection. You can pass any column name as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. (optional)
    show_sums = False # bool |  (optional) (default to False)

    try:
        # view aggregated result
        api_instance.view_aggregated_result(group_by=group_by, show_sums=show_sums)
    except Exception as e:
        print("Exception when calling CollectionsApi->view_aggregated_result: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **group_by** | **str**| The column to group by. Note: Aggregation is as of now only supported by the work package collection. You can pass any column name as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. | [optional] 
 **show_sums** | **bool**|  | [optional] [default to False]

### Return type

void (empty response body)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

