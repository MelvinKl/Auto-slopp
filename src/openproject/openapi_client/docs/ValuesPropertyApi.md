# openproject_client.ValuesPropertyApi

All URIs are relative to *https://openproject.melvin.beer*

Method | HTTP request | Description
------------- | ------------- | -------------
[**view_notification_detail**](ValuesPropertyApi.md#view_notification_detail) | **GET** /api/v3/notifications/{notification_id}/details/{id} | Get a notification detail
[**view_values_schema**](ValuesPropertyApi.md#view_values_schema) | **GET** /api/v3/values/schema/{id} | View Values schema


# **view_notification_detail**
> ValuesPropertyModel view_notification_detail(notification_id, id)

Get a notification detail

Returns an individual detail of a notification identified by the notification id and the id of the detail.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.values_property_model import ValuesPropertyModel
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
    api_instance = openproject_client.ValuesPropertyApi(api_client)
    notification_id = 1 # int | notification id
    id = 0 # int | detail id

    try:
        # Get a notification detail
        api_response = api_instance.view_notification_detail(notification_id, id)
        print("The response of ValuesPropertyApi->view_notification_detail:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ValuesPropertyApi->view_notification_detail: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **notification_id** | **int**| notification id | 
 **id** | **int**| detail id | 

### Return type

[**ValuesPropertyModel**](ValuesPropertyModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**404** | Returned if the notification or the detail of it does not exist or if the user does not have permission to view it.  **Required permission** being recipient of the notification |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **view_values_schema**
> SchemaModel view_values_schema(id)

View Values schema

The schema of a `Values` resource.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.schema_model import SchemaModel
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
    api_instance = openproject_client.ValuesPropertyApi(api_client)
    id = 'startDate' # str | The identifier of the value. This is typically the value of the `property` property of the `Values` resource. It should be in lower camelcase format.

    try:
        # View Values schema
        api_response = api_instance.view_values_schema(id)
        print("The response of ValuesPropertyApi->view_values_schema:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ValuesPropertyApi->view_values_schema: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| The identifier of the value. This is typically the value of the &#x60;property&#x60; property of the &#x60;Values&#x60; resource. It should be in lower camelcase format. | 

### Return type

[**SchemaModel**](SchemaModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**404** | Returned if the schema does not exist. |  -  |
**400** | Returned if the requested property id is not in a lower camel case format. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

