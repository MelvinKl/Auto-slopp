# auto_slopp.openproject.openapi_client.ProjectPhasesApi

All URIs are relative to *https://openproject.melvin.beer*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_project_phase**](ProjectPhasesApi.md#get_project_phase) | **GET** /api/v3/project_phases/{id} | Get a project phase


# **get_project_phase**
> ProjectPhaseModel get_project_phase(id)

Get a project phase

Gets a project phase resource. This resource contains an instance of a ProjectPhaseDefinition within a project which can
then have project specific dates.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.project_phase_model import ProjectPhaseModel
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
    api_instance = auto_slopp.openproject.openapi_client.ProjectPhasesApi(api_client)
    id = 1337 # int | Project phase id

    try:
        # Get a project phase
        api_response = api_instance.get_project_phase(id)
        print("The response of ProjectPhasesApi->get_project_phase:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProjectPhasesApi->get_project_phase: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Project phase id | 

### Return type

[**ProjectPhaseModel**](ProjectPhaseModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**404** | Returned if the project phase does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view project phase |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

