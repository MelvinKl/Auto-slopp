# auto_slopp.openproject.openapi_client.GroupsApi

All URIs are relative to *https://openproject.melvin.beer*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_group**](GroupsApi.md#create_group) | **POST** /api/v3/groups | Create group
[**delete_group**](GroupsApi.md#delete_group) | **DELETE** /api/v3/groups/{id} | Delete group
[**get_group**](GroupsApi.md#get_group) | **GET** /api/v3/groups/{id} | Get group
[**list_groups**](GroupsApi.md#list_groups) | **GET** /api/v3/groups | List groups
[**update_group**](GroupsApi.md#update_group) | **PATCH** /api/v3/groups/{id} | Update group


# **create_group**
> GroupModel create_group(group_write_model=group_write_model)

Create group

Creates a new group applying the attributes provided in the body.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.group_model import GroupModel
from auto_slopp.openproject.openapi_client.models.group_write_model import GroupWriteModel
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
    api_instance = auto_slopp.openproject.openapi_client.GroupsApi(api_client)
    group_write_model = auto_slopp.openproject.openapi_client.GroupWriteModel() # GroupWriteModel |  (optional)

    try:
        # Create group
        api_response = api_instance.create_group(group_write_model=group_write_model)
        print("The response of GroupsApi->create_group:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling GroupsApi->create_group: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **group_write_model** | [**GroupWriteModel**](GroupWriteModel.md)|  | [optional] 

### Return type

[**GroupModel**](GroupModel.md)

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
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** Administrator |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |
**422** | Returned if:  * a constraint for a property was violated (&#x60;PropertyConstraintViolation&#x60;) |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_group**
> delete_group(id)

Delete group

Deletes the group.

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
    api_instance = auto_slopp.openproject.openapi_client.GroupsApi(api_client)
    id = 1 # int | Group id

    try:
        # Delete group
        api_instance.delete_group(id)
    except Exception as e:
        print("Exception when calling GroupsApi->delete_group: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Group id | 

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
**202** | Returned if the group was marked for deletion.  Note that the response body is empty as of now. In future versions of the API a body *might* be returned, indicating the progress of deletion. |  -  |
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** Administrator |  -  |
**404** | Returned if the group does not exist or the client does not have sufficient permissions to see it.  **Required permission:** Administrator  *Note: A client without sufficient permissions shall not be able to test for the existence of a version. That&#39;s why a 404 is returned here, even if a 403 might be more appropriate.* |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_group**
> GroupModel get_group(id)

Get group

Fetches a group resource.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.group_model import GroupModel
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
    api_instance = auto_slopp.openproject.openapi_client.GroupsApi(api_client)
    id = 1 # int | Group id

    try:
        # Get group
        api_response = api_instance.get_group(id)
        print("The response of GroupsApi->get_group:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling GroupsApi->get_group: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Group id | 

### Return type

[**GroupModel**](GroupModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**404** | Returned if the group does not exist or if the API user does not have permission to view them.  **Required permission** If the user has the *manage members* permission in at least one project the user will be able to query all groups. If not, the user will be able to query all groups which are members in projects, he has the *view members* permission in. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_groups**
> GroupCollectionModel list_groups(sort_by=sort_by, select=select)

List groups

Returns a collection of groups. The client can choose to filter the
groups similar to how work packages are filtered. In addition to the provided
filters, the server will reduce the result set to only contain groups, for which
the requesting client has sufficient permissions (*view_members*, *manage_members*).

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.group_collection_model import GroupCollectionModel
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
    api_instance = auto_slopp.openproject.openapi_client.GroupsApi(api_client)
    sort_by = '[["id", "asc"]]' # str | JSON specifying sort criteria. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported sorts are:  + id: Sort by primary key  + created_at: Sort by group creation datetime  + updated_at: Sort by the time the group was updated last (optional) (default to '[["id", "asc"]]')
    select = 'total,elements/name,elements/self,self' # str | Comma separated list of properties to include. (optional)

    try:
        # List groups
        api_response = api_instance.list_groups(sort_by=sort_by, select=select)
        print("The response of GroupsApi->list_groups:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling GroupsApi->list_groups: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sort_by** | **str**| JSON specifying sort criteria. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported sorts are:  + id: Sort by primary key  + created_at: Sort by group creation datetime  + updated_at: Sort by the time the group was updated last | [optional] [default to &#39;[[&quot;id&quot;, &quot;asc&quot;]]&#39;]
 **select** | **str**| Comma separated list of properties to include. | [optional] 

### Return type

[**GroupCollectionModel**](GroupCollectionModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** View members or manage members in any project |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_group**
> GroupModel update_group(id, group_write_model=group_write_model)

Update group

Updates the given group by applying the attributes provided in the body.

Please note that the `members` array provided will override the existing set of members (similar to a PUT). A
client thus has to provide the complete list of members the group is to have after the PATCH even if only one
member is to be added.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.group_model import GroupModel
from auto_slopp.openproject.openapi_client.models.group_write_model import GroupWriteModel
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
    api_instance = auto_slopp.openproject.openapi_client.GroupsApi(api_client)
    id = 1 # int | Group id
    group_write_model = auto_slopp.openproject.openapi_client.GroupWriteModel() # GroupWriteModel |  (optional)

    try:
        # Update group
        api_response = api_instance.update_group(id, group_write_model=group_write_model)
        print("The response of GroupsApi->update_group:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling GroupsApi->update_group: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Group id | 
 **group_write_model** | [**GroupWriteModel**](GroupWriteModel.md)|  | [optional] 

### Return type

[**GroupModel**](GroupModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/hal+json, text/plain

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**400** | Occurs when the client did not send a valid JSON object in the request body. |  -  |
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** Administrator |  -  |
**404** | Returned if the group does not exist or the client does not have sufficient permissions to see it.  **Required permission** If the user has the *manage members* permission in at least one project the user will be able to query all groups. If not, the user will be able to query all groups which are members in projects, he has the *view members* permission in.  *Note: A client without sufficient permissions shall not be able to test for the existence of a version. That&#39;s why a 404 is returned here, even if a 403 might be more appropriate.* |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |
**422** | Returned if:  * a constraint for a property was violated (&#x60;PropertyConstraintViolation&#x60;) |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

