# auto_slopp.openproject.openapi_client.ActionsCapabilitiesApi

All URIs are relative to *https://openproject.melvin.beer*

Method | HTTP request | Description
------------- | ------------- | -------------
[**list_actions**](ActionsCapabilitiesApi.md#list_actions) | **GET** /api/v3/actions | List actions
[**list_capabilities**](ActionsCapabilitiesApi.md#list_capabilities) | **GET** /api/v3/capabilities | List capabilities
[**view_action**](ActionsCapabilitiesApi.md#view_action) | **GET** /api/v3/actions/{id} | View action
[**view_capabilities**](ActionsCapabilitiesApi.md#view_capabilities) | **GET** /api/v3/capabilities/{id} | View capabilities
[**view_global_context**](ActionsCapabilitiesApi.md#view_global_context) | **GET** /api/v3/capabilities/context/global | View global context


# **list_actions**
> object list_actions(filters=filters, sort_by=sort_by)

List actions

Returns a collection of actions. The client can choose to filter the actions similar to how work packages are filtered.
In addition to the provided filters, the server will reduce the result set to only contain actions, for which the requesting client
has sufficient permissions.

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
    api_instance = auto_slopp.openproject.openapi_client.ActionsCapabilitiesApi(api_client)
    filters = '[{ \"id\": { \"operator\": \"=\", \"values\": [\"memberships/create\"] }\" }]' # str | JSON specifying filter conditions. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported filters are:  + id: Returns only the action having the id or all actions except those having the id(s). (optional)
    sort_by = '[["id", "asc"]]' # str | JSON specifying sort criteria. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported sorts are:  + *No sort supported yet* (optional) (default to '[["id", "asc"]]')

    try:
        # List actions
        api_response = api_instance.list_actions(filters=filters, sort_by=sort_by)
        print("The response of ActionsCapabilitiesApi->list_actions:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ActionsCapabilitiesApi->list_actions: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **filters** | **str**| JSON specifying filter conditions. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported filters are:  + id: Returns only the action having the id or all actions except those having the id(s). | [optional] 
 **sort_by** | **str**| JSON specifying sort criteria. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported sorts are:  + *No sort supported yet* | [optional] [default to &#39;[[&quot;id&quot;, &quot;asc&quot;]]&#39;]

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

# **list_capabilities**
> object list_capabilities(filters=filters, sort_by=sort_by)

List capabilities

Returns a collection of actions assigned to a principal in a context. The client can choose to filter the actions similar to how work packages are filtered. In addition to the provided filters, the server will reduce the result set to only contain actions, for which the requesting client has sufficient permissions

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
    api_instance = auto_slopp.openproject.openapi_client.ActionsCapabilitiesApi(api_client)
    filters = '[{ \"principal\": { \"operator\": \"=\", \"values\": [\"1\"] }\" }]' # str | JSON specifying filter conditions. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint.  + action: Get all capabilities of a certain action  + principal: Get all capabilities of a principal  + context: Get all capabilities within a context. Note that for a workspace context the client needs to   provide `w{id}`, e.g. `w5` and for the global context a `g`.    + **Deprecation**: The now deprecated context `p` for project still works, but must eventually be replaced     with the `w` for the workspace context. (optional)
    sort_by = '[["id", "asc"]]' # str | JSON specifying sort criteria. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported sorts are:  + id: Sort by the capabilities id (optional) (default to '[["id", "asc"]]')

    try:
        # List capabilities
        api_response = api_instance.list_capabilities(filters=filters, sort_by=sort_by)
        print("The response of ActionsCapabilitiesApi->list_capabilities:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ActionsCapabilitiesApi->list_capabilities: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **filters** | **str**| JSON specifying filter conditions. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint.  + action: Get all capabilities of a certain action  + principal: Get all capabilities of a principal  + context: Get all capabilities within a context. Note that for a workspace context the client needs to   provide &#x60;w{id}&#x60;, e.g. &#x60;w5&#x60; and for the global context a &#x60;g&#x60;.    + **Deprecation**: The now deprecated context &#x60;p&#x60; for project still works, but must eventually be replaced     with the &#x60;w&#x60; for the workspace context. | [optional] 
 **sort_by** | **str**| JSON specifying sort criteria. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported sorts are:  + id: Sort by the capabilities id | [optional] [default to &#39;[[&quot;id&quot;, &quot;asc&quot;]]&#39;]

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

# **view_action**
> object view_action(id)

View action

Returns an individual action.

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
    api_instance = auto_slopp.openproject.openapi_client.ActionsCapabilitiesApi(api_client)
    id = 'work_packages/create' # str | action id which is the name of the action

    try:
        # View action
        api_response = api_instance.view_action(id)
        print("The response of ActionsCapabilitiesApi->view_action:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ActionsCapabilitiesApi->view_action: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| action id which is the name of the action | 

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
**404** | Returned if the action does not exist. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **view_capabilities**
> object view_capabilities(id)

View capabilities



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
    api_instance = auto_slopp.openproject.openapi_client.ActionsCapabilitiesApi(api_client)
    id = 'work_packages/create/p123-567' # str | capability id

    try:
        # View capabilities
        api_response = api_instance.view_capabilities(id)
        print("The response of ActionsCapabilitiesApi->view_capabilities:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ActionsCapabilitiesApi->view_capabilities: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| capability id | 

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
**404** | Returned if the capability does not exist. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **view_global_context**
> object view_global_context()

View global context

Returns the global capability context. This context is necessary to consistently link to a context even if the context is not a project.

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
    api_instance = auto_slopp.openproject.openapi_client.ActionsCapabilitiesApi(api_client)

    try:
        # View global context
        api_response = api_instance.view_global_context()
        print("The response of ActionsCapabilitiesApi->view_global_context:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ActionsCapabilitiesApi->view_global_context: %s\n" % e)
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
**404** | Returned if the action does not exist. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

