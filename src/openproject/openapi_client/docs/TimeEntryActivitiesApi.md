# openproject_client.TimeEntryActivitiesApi

All URIs are relative to *https://openproject.melvin.beer*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_time_entries_activity**](TimeEntryActivitiesApi.md#get_time_entries_activity) | **GET** /api/v3/time_entries/activity/{id} | View time entries activity


# **get_time_entries_activity**
> TimeEntryActivityModel get_time_entries_activity(id)

View time entries activity

Fetches the time entry activity resource by the given id.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.time_entry_activity_model import TimeEntryActivityModel
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
    api_instance = openproject_client.TimeEntryActivitiesApi(api_client)
    id = 1 # int | Time entries activity id

    try:
        # View time entries activity
        api_response = api_instance.get_time_entries_activity(id)
        print("The response of TimeEntryActivitiesApi->get_time_entries_activity:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TimeEntryActivitiesApi->get_time_entries_activity: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Time entries activity id | 

### Return type

[**TimeEntryActivityModel**](TimeEntryActivityModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**404** | Returned if the activity does not exist or if the user does not have permission to view them.  **Required permission** &#x60;view time entries&#x60;, &#x60;log time&#x60;, &#x60;edit time entries&#x60;, &#x60;edit own time entries&#x60; or &#x60;manage project activities&#x60; in any project |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

