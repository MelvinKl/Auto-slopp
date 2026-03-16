# auto_slopp.openproject.openapi_client.UserPreferencesApi

All URIs are relative to *https://openproject.melvin.beer*

Method | HTTP request | Description
------------- | ------------- | -------------
[**show_my_preferences**](UserPreferencesApi.md#show_my_preferences) | **GET** /api/v3/my_preferences | Show my preferences
[**update_user_preferences**](UserPreferencesApi.md#update_user_preferences) | **PATCH** /api/v3/my_preferences | Update my preferences


# **show_my_preferences**
> object show_my_preferences()

Show my preferences



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
    api_instance = auto_slopp.openproject.openapi_client.UserPreferencesApi(api_client)

    try:
        # Show my preferences
        api_response = api_instance.show_my_preferences()
        print("The response of UserPreferencesApi->show_my_preferences:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UserPreferencesApi->show_my_preferences: %s\n" % e)
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
**401** | Returned if no user is currently authenticated |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_user_preferences**
> object update_user_preferences(update_user_preferences_request=update_user_preferences_request)

Update my preferences

When calling this endpoint the client provides a single object, containing the properties that it wants to change, in the body.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.update_user_preferences_request import UpdateUserPreferencesRequest
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
    api_instance = auto_slopp.openproject.openapi_client.UserPreferencesApi(api_client)
    update_user_preferences_request = auto_slopp.openproject.openapi_client.UpdateUserPreferencesRequest() # UpdateUserPreferencesRequest |  (optional)

    try:
        # Update my preferences
        api_response = api_instance.update_user_preferences(update_user_preferences_request=update_user_preferences_request)
        print("The response of UserPreferencesApi->update_user_preferences:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UserPreferencesApi->update_user_preferences: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **update_user_preferences_request** | [**UpdateUserPreferencesRequest**](UpdateUserPreferencesRequest.md)|  | [optional] 

### Return type

**object**

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/hal+json, text/plain

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**400** | Occurs when the client did not send a valid JSON object in the request body. |  -  |
**401** | Returned if no user is currently authenticated |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |
**422** | Returned if the update contains invalid properties. Reasons are:  * Specifying an invalid type  * Using an unknown time zone |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

