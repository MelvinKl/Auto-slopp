# openproject_client.RolesApi

All URIs are relative to *https://openproject.melvin.beer*

Method | HTTP request | Description
------------- | ------------- | -------------
[**list_roles**](RolesApi.md#list_roles) | **GET** /api/v3/roles | List roles
[**view_role**](RolesApi.md#view_role) | **GET** /api/v3/roles/{id} | View role


# **list_roles**
> object list_roles(filters=filters)

List roles

List all defined roles. This includes built in roles like 'Anonymous' and 'Non member'.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
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
    api_instance = openproject_client.RolesApi(api_client)
    filters = '[{ \"unit\": { \"operator\": \"=\", \"values\": [\"system\"] }\" }]' # str | JSON specifying filter conditions. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported filters are:  + grantable: filters roles based on whether they are selectable for a membership  + unit: filters roles based on the unit ('project' or 'system') for which they are selectable for a membership (optional)

    try:
        # List roles
        api_response = api_instance.list_roles(filters=filters)
        print("The response of RolesApi->list_roles:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RolesApi->list_roles: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **filters** | **str**| JSON specifying filter conditions. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported filters are:  + grantable: filters roles based on whether they are selectable for a membership  + unit: filters roles based on the unit (&#39;project&#39; or &#39;system&#39;) for which they are selectable for a membership | [optional] 

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **view_role**
> RoleModel view_role(id)

View role

Fetch an individual role.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.role_model import RoleModel
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
    api_instance = openproject_client.RolesApi(api_client)
    id = 1 # int | Role id

    try:
        # View role
        api_response = api_instance.view_role(id)
        print("The response of RolesApi->view_role:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RolesApi->view_role: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Role id | 

### Return type

[**RoleModel**](RoleModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**403** | Returned if the client does not have sufficient permissions to see roles.  **Required permission:** view members **or** manage members |  -  |
**404** | Returned if the role does not exist. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

