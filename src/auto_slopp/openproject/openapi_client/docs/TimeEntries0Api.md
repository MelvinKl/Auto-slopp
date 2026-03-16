# auto_slopp.openproject.openapi_client.TimeEntriesApi

All URIs are relative to *https://openproject.melvin.beer*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_time_entry**](TimeEntriesApi.md#create_time_entry) | **POST** /api/v3/time_entries | Create time entry
[**delete_time_entry**](TimeEntriesApi.md#delete_time_entry) | **DELETE** /api/v3/time_entries/{id} | Delete time entry
[**get_time_entry**](TimeEntriesApi.md#get_time_entry) | **GET** /api/v3/time_entries/{id} | Get time entry
[**list_time_entries**](TimeEntriesApi.md#list_time_entries) | **GET** /api/v3/time_entries | List time entries


# **create_time_entry**
> TimeEntryModel create_time_entry(time_entry_model=time_entry_model)

Create time entry

Creates a new time entry applying the attributes provided in the body.
Please note that while there is a fixed set of attributes, custom fields can extend
a time entries' attributes and are accepted by the endpoint.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.time_entry_model import TimeEntryModel
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
    api_instance = auto_slopp.openproject.openapi_client.TimeEntriesApi(api_client)
    time_entry_model = auto_slopp.openproject.openapi_client.TimeEntryModel() # TimeEntryModel |  (optional)

    try:
        # Create time entry
        api_response = api_instance.create_time_entry(time_entry_model=time_entry_model)
        print("The response of TimeEntriesApi->create_time_entry:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TimeEntriesApi->create_time_entry: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **time_entry_model** | [**TimeEntryModel**](TimeEntryModel.md)|  | [optional] 

### Return type

[**TimeEntryModel**](TimeEntryModel.md)

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
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** Log time |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |
**422** | Returned if:  * a constraint for a property was violated (&#x60;PropertyConstraintViolation&#x60;) |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_time_entry**
> delete_time_entry(id)

Delete time entry

Permanently deletes the specified time entry.

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
    api_instance = auto_slopp.openproject.openapi_client.TimeEntriesApi(api_client)
    id = 1 # int | Time entry id

    try:
        # Delete time entry
        api_instance.delete_time_entry(id)
    except Exception as e:
        print("Exception when calling TimeEntriesApi->delete_time_entry: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Time entry id | 

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
**204** | Returned if the time entry was deleted successfully. |  -  |
**403** | Returned if the client does not have sufficient permissions |  -  |
**404** | Returned if the time entry does not exist or if the user does not have sufficient permissions to see the time entry.  **Required permission** &#x60;view time entries&#x60; in the project the time entry is assigned to or &#x60;view own time entries&#x60; for time entries belonging to the user |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_time_entry**
> TimeEntryModel get_time_entry(id)

Get time entry

Retrieves a single time entry identified by the given id.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.time_entry_model import TimeEntryModel
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
    api_instance = auto_slopp.openproject.openapi_client.TimeEntriesApi(api_client)
    id = 1 # int | time entry id

    try:
        # Get time entry
        api_response = api_instance.get_time_entry(id)
        print("The response of TimeEntriesApi->get_time_entry:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TimeEntriesApi->get_time_entry: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| time entry id | 

### Return type

[**TimeEntryModel**](TimeEntryModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**404** | Returned if the time entry does not exist or if the user does not have permission to view them.  **Required permission** - &#x60;view time entries&#x60; in the project the time entry is assigned to or - &#x60;view own time entries&#x60; for time entries belonging to the user |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_time_entries**
> TimeEntryCollectionModel list_time_entries(offset=offset, page_size=page_size, sort_by=sort_by, filters=filters)

List time entries

Lists time entries. The time entries returned depend on the filters
provided and also on the permission of the requesting user.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.time_entry_collection_model import TimeEntryCollectionModel
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
    api_instance = auto_slopp.openproject.openapi_client.TimeEntriesApi(api_client)
    offset = 1 # int | Page number inside the requested collection. (optional) (default to 1)
    page_size = 25 # int | Number of elements to display per page. (optional)
    sort_by = '["spent_on", "asc"]' # str | JSON specifying sort criteria. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported sorts are:  + id: Sort by primary key  + hours: Sort by logged hours  + spent_on: Sort by spent on date  + created_at: Sort by time entry creation datetime  + updated_at: Sort by the time the time entry was updated last (optional) (default to '["spent_on", "asc"]')
    filters = '[{ \"entity_type\": { \"operator\": \"=\", \"values\": [\"WorkPackage\"] }}, { \"entity_id\": { \"operator\": \"=\", \"values\": [\"1\", \"2\"] } }, { \"project\": { \"operator\": \"=\", \"values\": [\"1\"] } }]' # str | JSON specifying filter conditions. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported filters are:  + entity_type: Filter time entries depending on the entity they are logged on. Can either be `WorkPackage` or `Meeting`.  + entity_id: Filter time entries for the specified entity IDs.  + project_id: Filter time entries by project  + user_id: Filter time entries by users  + ongoing: Filter to only recevie ongoing timers  + spent_on: Filter time entries by spent on date  + created_at: Filter time entries by creation datetime  + updated_at: Filter time entries by the last time they where updated  + activity_id: Filter time entries by time entry activity (optional)

    try:
        # List time entries
        api_response = api_instance.list_time_entries(offset=offset, page_size=page_size, sort_by=sort_by, filters=filters)
        print("The response of TimeEntriesApi->list_time_entries:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TimeEntriesApi->list_time_entries: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **offset** | **int**| Page number inside the requested collection. | [optional] [default to 1]
 **page_size** | **int**| Number of elements to display per page. | [optional] 
 **sort_by** | **str**| JSON specifying sort criteria. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported sorts are:  + id: Sort by primary key  + hours: Sort by logged hours  + spent_on: Sort by spent on date  + created_at: Sort by time entry creation datetime  + updated_at: Sort by the time the time entry was updated last | [optional] [default to &#39;[&quot;spent_on&quot;, &quot;asc&quot;]&#39;]
 **filters** | **str**| JSON specifying filter conditions. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported filters are:  + entity_type: Filter time entries depending on the entity they are logged on. Can either be &#x60;WorkPackage&#x60; or &#x60;Meeting&#x60;.  + entity_id: Filter time entries for the specified entity IDs.  + project_id: Filter time entries by project  + user_id: Filter time entries by users  + ongoing: Filter to only recevie ongoing timers  + spent_on: Filter time entries by spent on date  + created_at: Filter time entries by creation datetime  + updated_at: Filter time entries by the last time they where updated  + activity_id: Filter time entries by time entry activity | [optional] 

### Return type

[**TimeEntryCollectionModel**](TimeEntryCollectionModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**400** | Occurs when the client did not send a valid JSON object in the request body. |  -  |
**403** | Returned if the client is not logged in and login is required. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

