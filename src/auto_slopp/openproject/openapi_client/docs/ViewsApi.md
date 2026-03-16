# auto_slopp.openproject.openapi_client.ViewsApi

All URIs are relative to *https://openproject.melvin.beer*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_views**](ViewsApi.md#create_views) | **POST** /api/v3/views/{id} | Create view
[**list_views**](ViewsApi.md#list_views) | **GET** /api/v3/views | List views
[**view_view**](ViewsApi.md#view_view) | **GET** /api/v3/views/{id} | View view


# **create_views**
> object create_views(id, create_views_request=create_views_request)

Create view

When calling this endpoint the client provides a single object, containing at least the properties and links that are required, in the body.
The required fields of a View can be found in its schema, which is embedded in the respective form.
Note that it is only allowed to provide properties or links supporting the write operation.

There are different subtypes of `Views` (e.g. `Views::WorkPackagesTable`) with each having its own
endpoint for creating that subtype e.g.

* `/api/v3/views/work_packages_table` for `Views::WorkPackagesTable`
* `/api/v3/views/team_planner` for `Views::TeamPlanner`
* `/api/v3/views/work_packages_calendar` for `Views::WorkPackagesCalendar`

**Not yet implemented** To get the list of available subtypes and by that the endpoints for creating a subtype, use the
```
  /api/v3/views/schemas
```
endpoint.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.create_views_request import CreateViewsRequest
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
    api_instance = auto_slopp.openproject.openapi_client.ViewsApi(api_client)
    id = '1' # str | The view identifier
    create_views_request = {"_links":{"query":{"href":"/api/v3/queries/5"}}} # CreateViewsRequest |  (optional)

    try:
        # Create view
        api_response = api_instance.create_views(id, create_views_request=create_views_request)
        print("The response of ViewsApi->create_views:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ViewsApi->create_views: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| The view identifier | 
 **create_views_request** | [**CreateViewsRequest**](CreateViewsRequest.md)|  | [optional] 

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
**201** | Created |  -  |
**400** | Occurs when the client did not send a valid JSON object in the request body. |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |
**422** | Returned if:  * the client tries to modify a read-only property (&#x60;PropertyIsReadOnly&#x60;)  * a constraint for a property was violated (&#x60;PropertyConstraintViolation&#x60;)  * the client provides a link to an invalid resource (&#x60;ResourceTypeMismatch&#x60;),   e.g. a query not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_views**
> list_views(filters=filters)

List views

Returns a collection of Views. The collection can be filtered via query parameters similar to how work packages are filtered.

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
    api_instance = auto_slopp.openproject.openapi_client.ViewsApi(api_client)
    filters = '[{ \"project_id\": { \"operator\": \"!*\", \"values\": null }\" }]' # str | JSON specifying filter conditions. Currently supported filters are:  + project: filters views by the project their associated query is assigned to. If the project filter is passed with the `!*` (not any) operator, global views are returned.  + id: filters views based on their id  + type: filters views based on their type (optional)

    try:
        # List views
        api_instance.list_views(filters=filters)
    except Exception as e:
        print("Exception when calling ViewsApi->list_views: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **filters** | **str**| JSON specifying filter conditions. Currently supported filters are:  + project: filters views by the project their associated query is assigned to. If the project filter is passed with the &#x60;!*&#x60; (not any) operator, global views are returned.  + id: filters views based on their id  + type: filters views based on their type | [optional] 

### Return type

void (empty response body)

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

# **view_view**
> view_view(id)

View view



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
    api_instance = auto_slopp.openproject.openapi_client.ViewsApi(api_client)
    id = 42 # int | View id

    try:
        # View view
        api_instance.view_view(id)
    except Exception as e:
        print("Exception when calling ViewsApi->view_view: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| View id | 

### Return type

void (empty response body)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Returns the result of a single view, dependent of the view type. |  -  |
**400** | Occurs when the client did not send a valid JSON object in the request body. |  -  |
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** The required permission depends on the type of the view. |  -  |
**404** | Returned if the resource can not be found.  *Note: A client without sufficient permissions shall not be able to test for the existence of a view. That&#39;s why a 404 is returned here, even if a 403 might be more appropriate.* |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

