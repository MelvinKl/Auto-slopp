# openproject_client.ProjectPhaseDefinitionsApi

All URIs are relative to *https://openproject.melvin.beer*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_project_phase_definition**](ProjectPhaseDefinitionsApi.md#get_project_phase_definition) | **GET** /api/v3/project_phase_definitions/{id} | Get a project phase definition
[**list_project_phase_definitions**](ProjectPhaseDefinitionsApi.md#list_project_phase_definitions) | **GET** /api/v3/project_phase_definitions | List project phase definitions


# **get_project_phase_definition**
> ProjectPhaseDefinitionModel get_project_phase_definition(id)

Get a project phase definition

Gets a project phase definition resource. This resource is part of the abstract definition of a project life
cycle shaping the phases of a project. 

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.project_phase_definition_model import ProjectPhaseDefinitionModel
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
    api_instance = openproject_client.ProjectPhaseDefinitionsApi(api_client)
    id = 1337 # int | Project phase definition id

    try:
        # Get a project phase definition
        api_response = api_instance.get_project_phase_definition(id)
        print("The response of ProjectPhaseDefinitionsApi->get_project_phase_definition:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProjectPhaseDefinitionsApi->get_project_phase_definition: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Project phase definition id | 

### Return type

[**ProjectPhaseDefinitionModel**](ProjectPhaseDefinitionModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**404** | Returned if the user does not have permission to see project phases.  **Required permission:** view project phase OR select project phase |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_project_phase_definitions**
> ProjectPhaseDefinitionCollectionModel list_project_phase_definitions()

List project phase definitions

Returns a collection of all project phase definitions.
The result set is always limited to only contain project phase definitions the client is allowed to see.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.project_phase_definition_collection_model import ProjectPhaseDefinitionCollectionModel
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
    api_instance = openproject_client.ProjectPhaseDefinitionsApi(api_client)

    try:
        # List project phase definitions
        api_response = api_instance.list_project_phase_definitions()
        print("The response of ProjectPhaseDefinitionsApi->list_project_phase_definitions:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProjectPhaseDefinitionsApi->list_project_phase_definitions: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**ProjectPhaseDefinitionCollectionModel**](ProjectPhaseDefinitionCollectionModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**400** | Returned if the client sends invalid request parameters e.g. filters |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

