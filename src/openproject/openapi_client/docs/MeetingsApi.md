# openproject_client.MeetingsApi

All URIs are relative to *https://openproject.melvin.beer*

Method | HTTP request | Description
------------- | ------------- | -------------
[**view_meeting**](MeetingsApi.md#view_meeting) | **GET** /api/v3/meetings/{id} | View Meeting Page


# **view_meeting**
> MeetingModel view_meeting(id)

View Meeting Page

Retrieve an individual meeting as identified by the id parameter

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.meeting_model import MeetingModel
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
    api_instance = openproject_client.MeetingsApi(api_client)
    id = 1 # int | Meeting identifier

    try:
        # View Meeting Page
        api_response = api_instance.view_meeting(id)
        print("The response of MeetingsApi->view_meeting:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MeetingsApi->view_meeting: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Meeting identifier | 

### Return type

[**MeetingModel**](MeetingModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**404** | Returned if the meeting does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view meetings in the page&#39;s project |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

