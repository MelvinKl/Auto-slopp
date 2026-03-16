# openproject_client.CustomActionsApi

All URIs are relative to *https://openproject.melvin.beer*

Method | HTTP request | Description
------------- | ------------- | -------------
[**execute_custom_action**](CustomActionsApi.md#execute_custom_action) | **POST** /api/v3/custom_actions/{id}/execute | Execute custom action
[**get_custom_action**](CustomActionsApi.md#get_custom_action) | **GET** /api/v3/custom_actions/{id} | Get a custom action


# **execute_custom_action**
> execute_custom_action(id, execute_custom_action_request=execute_custom_action_request)

Execute custom action

A POST to this endpoint executes the custom action on the work package provided in the payload. The altered work package will be returned. In order to avoid executing
 the custom action unbeknown to a change that has already taken place, the client has to provide the work package's current lockVersion.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.execute_custom_action_request import ExecuteCustomActionRequest
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
    api_instance = openproject_client.CustomActionsApi(api_client)
    id = 1 # int | The id of the custom action to execute
    execute_custom_action_request = openproject_client.ExecuteCustomActionRequest() # ExecuteCustomActionRequest |  (optional)

    try:
        # Execute custom action
        api_instance.execute_custom_action(id, execute_custom_action_request=execute_custom_action_request)
    except Exception as e:
        print("Exception when calling CustomActionsApi->execute_custom_action: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| The id of the custom action to execute | 
 **execute_custom_action_request** | [**ExecuteCustomActionRequest**](ExecuteCustomActionRequest.md)|  | [optional] 

### Return type

void (empty response body)

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
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** edit work packages - Additional permissions might be required based on the custom action. |  -  |
**404** | Returned if the custom action does not exist. |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**409** | Returned if the client provided an outdated lockVersion or no lockVersion at all. |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |
**422** | Returned if the custom action was not executed successfully e.g. when a constraint on a work package property was violated. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_custom_action**
> CustomActionModel get_custom_action(id)

Get a custom action

Retrieves a custom action by id.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.custom_action_model import CustomActionModel
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
    api_instance = openproject_client.CustomActionsApi(api_client)
    id = 42 # int | The id of the custom action to fetch

    try:
        # Get a custom action
        api_response = api_instance.get_custom_action(id)
        print("The response of CustomActionsApi->get_custom_action:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CustomActionsApi->get_custom_action: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| The id of the custom action to fetch | 

### Return type

[**CustomActionModel**](CustomActionModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** edit work packages in any project |  -  |
**404** | Returned if the custom action does not exist. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

