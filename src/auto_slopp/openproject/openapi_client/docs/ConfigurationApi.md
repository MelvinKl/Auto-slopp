# auto_slopp.openproject.openapi_client.ConfigurationApi

All URIs are relative to *https://openproject.melvin.beer*

Method | HTTP request | Description
------------- | ------------- | -------------
[**view_configuration**](ConfigurationApi.md#view_configuration) | **GET** /api/v3/configuration | View configuration
[**view_project_configuration**](ConfigurationApi.md#view_project_configuration) | **GET** /api/v3/projects/{id}/configuration | View project configuration


# **view_configuration**
> ConfigurationModel view_configuration()

View configuration



### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.configuration_model import ConfigurationModel
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
    api_instance = auto_slopp.openproject.openapi_client.ConfigurationApi(api_client)

    try:
        # View configuration
        api_response = api_instance.view_configuration()
        print("The response of ConfigurationApi->view_configuration:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ConfigurationApi->view_configuration: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**ConfigurationModel**](ConfigurationModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **view_project_configuration**
> ProjectConfigurationModel view_project_configuration(id)

View project configuration

Returns the configuration scoped to a specific project, including all global
configuration properties plus project-specific settings.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.project_configuration_model import ProjectConfigurationModel
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
    api_instance = auto_slopp.openproject.openapi_client.ConfigurationApi(api_client)
    id = 1 # int | Project id

    try:
        # View project configuration
        api_response = api_instance.view_project_configuration(id)
        print("The response of ConfigurationApi->view_project_configuration:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ConfigurationApi->view_project_configuration: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Project id | 

### Return type

[**ProjectConfigurationModel**](ProjectConfigurationModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**404** | Returned if the project does not exist or the user cannot view it. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

