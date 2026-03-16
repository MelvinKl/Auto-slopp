# openproject_client.NotificationsApi

All URIs are relative to *https://openproject.melvin.beer*

Method | HTTP request | Description
------------- | ------------- | -------------
[**list_notifications**](NotificationsApi.md#list_notifications) | **GET** /api/v3/notifications | Get notification collection
[**read_notification**](NotificationsApi.md#read_notification) | **POST** /api/v3/notifications/{id}/read_ian | Read notification
[**read_notifications**](NotificationsApi.md#read_notifications) | **POST** /api/v3/notifications/read_ian | Read all notifications
[**unread_notification**](NotificationsApi.md#unread_notification) | **POST** /api/v3/notifications/{id}/unread_ian | Unread notification
[**unread_notifications**](NotificationsApi.md#unread_notifications) | **POST** /api/v3/notifications/unread_ian | Unread all notifications
[**view_notification**](NotificationsApi.md#view_notification) | **GET** /api/v3/notifications/{id} | Get the notification
[**view_notification_detail**](NotificationsApi.md#view_notification_detail) | **GET** /api/v3/notifications/{notification_id}/details/{id} | Get a notification detail


# **list_notifications**
> NotificationCollectionModel list_notifications(offset=offset, page_size=page_size, sort_by=sort_by, group_by=group_by, filters=filters)

Get notification collection

Returns the collection of available in-app notifications. The notifications returned depend on the provided
parameters and also on the requesting user's permissions.

Contrary to most collections, this one also links to and embeds schemas for the `details` properties of the notifications returned.
This is an optimization. Clients will receive the information necessary to display the various types of details that a notification
can carry.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.notification_collection_model import NotificationCollectionModel
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
    api_instance = openproject_client.NotificationsApi(api_client)
    offset = 1 # int | Page number inside the requested collection. (optional) (default to 1)
    page_size = 20 # int | Number of elements to display per page. (optional) (default to 20)
    sort_by = '[[\"reason\", \"asc\"]]' # str | JSON specifying sort criteria. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported sorts are:  + id: Sort by primary key  + reason: Sort by notification reason  + readIAN: Sort by read status (optional)
    group_by = 'reason' # str | string specifying group_by criteria.  + reason: Group by notification reason  + project: Sort by associated project (optional)
    filters = '[{ \"readIAN\": { \"operator\": \"=\", \"values\": [\"t\"] } }]' # str | JSON specifying filter conditions. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported filters are:  + id: Filter by primary key  + project: Filter by the project the notification was created in  + readIAN: Filter by read status  + reason: Filter by the reason, e.g. 'mentioned' or 'assigned' the notification was created because of  + resourceId: Filter by the id of the resource the notification was created for. Ideally used together with the `resourceType` filter.  + resourceType: Filter by the type of the resource the notification was created for. Ideally used together with the `resourceId` filter. (optional)

    try:
        # Get notification collection
        api_response = api_instance.list_notifications(offset=offset, page_size=page_size, sort_by=sort_by, group_by=group_by, filters=filters)
        print("The response of NotificationsApi->list_notifications:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling NotificationsApi->list_notifications: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **offset** | **int**| Page number inside the requested collection. | [optional] [default to 1]
 **page_size** | **int**| Number of elements to display per page. | [optional] [default to 20]
 **sort_by** | **str**| JSON specifying sort criteria. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported sorts are:  + id: Sort by primary key  + reason: Sort by notification reason  + readIAN: Sort by read status | [optional] 
 **group_by** | **str**| string specifying group_by criteria.  + reason: Group by notification reason  + project: Sort by associated project | [optional] 
 **filters** | **str**| JSON specifying filter conditions. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported filters are:  + id: Filter by primary key  + project: Filter by the project the notification was created in  + readIAN: Filter by read status  + reason: Filter by the reason, e.g. &#39;mentioned&#39; or &#39;assigned&#39; the notification was created because of  + resourceId: Filter by the id of the resource the notification was created for. Ideally used together with the &#x60;resourceType&#x60; filter.  + resourceType: Filter by the type of the resource the notification was created for. Ideally used together with the &#x60;resourceId&#x60; filter. | [optional] 

### Return type

[**NotificationCollectionModel**](NotificationCollectionModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**403** | Returned if the client is not logged in and login is required. |  -  |
**422** | Returned if the client sends invalid request parameters e.g. filters |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **read_notification**
> read_notification(id)

Read notification

Marks the given notification as read.

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
    api_instance = openproject_client.NotificationsApi(api_client)
    id = 1 # int | notification id

    try:
        # Read notification
        api_instance.read_notification(id)
    except Exception as e:
        print("Exception when calling NotificationsApi->read_notification: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| notification id | 

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
**204** | OK |  -  |
**404** | Returned if the notification does not exist or if the user does not have permission to view it.  **Required permission** being recipient of the notification |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **read_notifications**
> read_notifications(filters=filters)

Read all notifications

Marks the whole notification collection as read. The collection contains only elements the authenticated user can
see, and can be further reduced with filters.

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
    api_instance = openproject_client.NotificationsApi(api_client)
    filters = '[{ \"reason\": { \"operator\": \"=\", \"values\": [\"mentioned\"] } }]' # str | JSON specifying filter conditions. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported filters are:  + id: Filter by primary key  + project: Filter by the project the notification was created in  + reason: Filter by the reason, e.g. 'mentioned' or 'assigned' the notification was created because of  + resourceId: Filter by the id of the resource the notification was created for. Ideally used together with the   `resourceType` filter.  + resourceType: Filter by the type of the resource the notification was created for. Ideally used together with   the `resourceId` filter. (optional)

    try:
        # Read all notifications
        api_instance.read_notifications(filters=filters)
    except Exception as e:
        print("Exception when calling NotificationsApi->read_notifications: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **filters** | **str**| JSON specifying filter conditions. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported filters are:  + id: Filter by primary key  + project: Filter by the project the notification was created in  + reason: Filter by the reason, e.g. &#39;mentioned&#39; or &#39;assigned&#39; the notification was created because of  + resourceId: Filter by the id of the resource the notification was created for. Ideally used together with the   &#x60;resourceType&#x60; filter.  + resourceType: Filter by the type of the resource the notification was created for. Ideally used together with   the &#x60;resourceId&#x60; filter. | [optional] 

### Return type

void (empty response body)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json, text/plain

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | OK |  -  |
**400** | Returned if the request is not properly formatted. |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **unread_notification**
> unread_notification(id)

Unread notification

Marks the given notification as unread.

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
    api_instance = openproject_client.NotificationsApi(api_client)
    id = 1 # int | notification id

    try:
        # Unread notification
        api_instance.unread_notification(id)
    except Exception as e:
        print("Exception when calling NotificationsApi->unread_notification: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| notification id | 

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
**204** | OK |  -  |
**404** | Returned if the notification does not exist or if the user does not have permission to view it.  **Required permission** being recipient of the notification |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **unread_notifications**
> unread_notifications(filters=filters)

Unread all notifications

Marks the whole notification collection as unread. The collection contains only elements the authenticated user can
see, and can be further reduced with filters.

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
    api_instance = openproject_client.NotificationsApi(api_client)
    filters = '[{ \"reason\": { \"operator\": \"=\", \"values\": [\"mentioned\"] } }]' # str | JSON specifying filter conditions. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported filters are:  + id: Filter by primary key  + project: Filter by the project the notification was created in  + reason: Filter by the reason, e.g. 'mentioned' or 'assigned' the notification was created because of  + resourceId: Filter by the id of the resource the notification was created for. Ideally used together with the   `resourceType` filter.  + resourceType: Filter by the type of the resource the notification was created for. Ideally used together with   the `resourceId` filter. (optional)

    try:
        # Unread all notifications
        api_instance.unread_notifications(filters=filters)
    except Exception as e:
        print("Exception when calling NotificationsApi->unread_notifications: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **filters** | **str**| JSON specifying filter conditions. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported filters are:  + id: Filter by primary key  + project: Filter by the project the notification was created in  + reason: Filter by the reason, e.g. &#39;mentioned&#39; or &#39;assigned&#39; the notification was created because of  + resourceId: Filter by the id of the resource the notification was created for. Ideally used together with the   &#x60;resourceType&#x60; filter.  + resourceType: Filter by the type of the resource the notification was created for. Ideally used together with   the &#x60;resourceId&#x60; filter. | [optional] 

### Return type

void (empty response body)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json, text/plain

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | OK |  -  |
**400** | Occurs when the client did not send a valid JSON object in the request body. |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **view_notification**
> NotificationModel view_notification(id)

Get the notification

Returns the notification identified by the notification id.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.notification_model import NotificationModel
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
    api_instance = openproject_client.NotificationsApi(api_client)
    id = 1 # int | notification id

    try:
        # Get the notification
        api_response = api_instance.view_notification(id)
        print("The response of NotificationsApi->view_notification:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling NotificationsApi->view_notification: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| notification id | 

### Return type

[**NotificationModel**](NotificationModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**404** | Returned if the notification does not exist or if the user does not have permission to view it.  **Required permission** being recipient of the notification |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

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
    api_instance = openproject_client.NotificationsApi(api_client)
    notification_id = 1 # int | notification id
    id = 0 # int | detail id

    try:
        # Get a notification detail
        api_response = api_instance.view_notification_detail(notification_id, id)
        print("The response of NotificationsApi->view_notification_detail:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling NotificationsApi->view_notification_detail: %s\n" % e)
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

