# openproject_client.CustomOptionsApi

All URIs are relative to *https://openproject.melvin.beer*

Method | HTTP request | Description
------------- | ------------- | -------------
[**view_custom_option**](CustomOptionsApi.md#view_custom_option) | **GET** /api/v3/custom_options/{id} | View Custom Option


# **view_custom_option**
> CustomOptionModel view_custom_option(id)

View Custom Option



### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.custom_option_model import CustomOptionModel
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
    api_instance = openproject_client.CustomOptionsApi(api_client)
    id = 1 # int | The custom option's identifier

    try:
        # View Custom Option
        api_response = api_instance.view_custom_option(id)
        print("The response of CustomOptionsApi->view_custom_option:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CustomOptionsApi->view_custom_option: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| The custom option&#39;s identifier | 

### Return type

[**CustomOptionModel**](CustomOptionModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**404** | Returned if the custom option does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view work package in any project the custom option&#39;s custom field is active in. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

