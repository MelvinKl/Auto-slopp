# auto_slopp.openproject.openapi_client.QueriesApi

All URIs are relative to *https://openproject.melvin.beer*

Method | HTTP request | Description
------------- | ------------- | -------------
[**available_projects_for_query**](QueriesApi.md#available_projects_for_query) | **GET** /api/v3/queries/available_projects | Available projects for query
[**create_query**](QueriesApi.md#create_query) | **POST** /api/v3/queries | Create query
[**delete_query**](QueriesApi.md#delete_query) | **DELETE** /api/v3/queries/{id} | Delete query
[**edit_query**](QueriesApi.md#edit_query) | **PATCH** /api/v3/queries/{id} | Edit Query
[**list_queries**](QueriesApi.md#list_queries) | **GET** /api/v3/queries | List queries
[**query_create_form**](QueriesApi.md#query_create_form) | **POST** /api/v3/queries/form | Query Create Form
[**query_update_form**](QueriesApi.md#query_update_form) | **POST** /api/v3/queries/{id}/form | Query Update Form
[**star_query**](QueriesApi.md#star_query) | **PATCH** /api/v3/queries/{id}/star | Star query
[**unstar_query**](QueriesApi.md#unstar_query) | **PATCH** /api/v3/queries/{id}/unstar | Unstar query
[**view_default_query**](QueriesApi.md#view_default_query) | **GET** /api/v3/queries/default | View default query
[**view_default_query_for_project**](QueriesApi.md#view_default_query_for_project) | **GET** /api/v3/projects/{id}/queries/default | View default query for project
[**view_default_query_for_workspace**](QueriesApi.md#view_default_query_for_workspace) | **GET** /api/v3/workspaces/{id}/queries/default | View default query for workspace
[**view_query**](QueriesApi.md#view_query) | **GET** /api/v3/queries/{id} | View query
[**view_schema_for_global_queries**](QueriesApi.md#view_schema_for_global_queries) | **GET** /api/v3/queries/schema | View schema for global queries
[**view_schema_for_project_queries**](QueriesApi.md#view_schema_for_project_queries) | **GET** /api/v3/projects/{id}/queries/schema | View schema for project queries
[**view_schema_for_workspace_queries**](QueriesApi.md#view_schema_for_workspace_queries) | **GET** /api/v3/workspace/{id}/queries/schema | View schema for workspace queries


# **available_projects_for_query**
> object available_projects_for_query()

Available projects for query

Gets a list of projects that are available as projects a query can be assigned to.

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
    api_instance = auto_slopp.openproject.openapi_client.QueriesApi(api_client)

    try:
        # Available projects for query
        api_response = api_instance.available_projects_for_query()
        print("The response of QueriesApi->available_projects_for_query:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling QueriesApi->available_projects_for_query: %s\n" % e)
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
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** view work packages |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_query**
> QueryModel create_query(query_create_form=query_create_form)

Create query

When calling this endpoint the client provides a single object, containing at least the properties and links that are required, in the body.
The required fields of a Query can be found in its schema, which is embedded in the respective form.
Note that it is only allowed to provide properties or links supporting the write operation.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.query_create_form import QueryCreateForm
from auto_slopp.openproject.openapi_client.models.query_model import QueryModel
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
    api_instance = auto_slopp.openproject.openapi_client.QueriesApi(api_client)
    query_create_form = auto_slopp.openproject.openapi_client.QueryCreateForm() # QueryCreateForm |  (optional)

    try:
        # Create query
        api_response = api_instance.create_query(query_create_form=query_create_form)
        print("The response of QueriesApi->create_query:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling QueriesApi->create_query: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **query_create_form** | [**QueryCreateForm**](QueryCreateForm.md)|  | [optional] 

### Return type

[**QueryModel**](QueryModel.md)

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
**422** | Returned if:  * the client tries to modify a read-only property (&#x60;PropertyIsReadOnly&#x60;)  * a constraint for a property was violated (&#x60;PropertyConstraintViolation&#x60;)  * the client provides a link to an invalid resource (&#x60;ResourceTypeMismatch&#x60;),   e.g. a user, project or operator not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_query**
> delete_query(id)

Delete query

Delete the query identified by the id parameter

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
    api_instance = auto_slopp.openproject.openapi_client.QueriesApi(api_client)
    id = 1 # int | Query id

    try:
        # Delete query
        api_instance.delete_query(id)
    except Exception as e:
        print("Exception when calling QueriesApi->delete_query: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Query id | 

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
**204** | No Content |  -  |
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** for own queries none; for public queries: manage public queries  *Note that you will only receive this error, if you are at least allowed to see the corresponding query.* |  -  |
**404** | Returned if the query does not exist or the client does not have sufficient permissions to see it.  **Required condition:** query belongs to user or query is public  **Required permission:** view work package in queries project |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **edit_query**
> QueryModel edit_query(id, query_update_form=query_update_form)

Edit Query

When calling this endpoint the client provides a single object, containing the properties and links that it wants to change, in the body.
Note that it is only allowed to provide properties or links supporting the **write** operation.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.query_model import QueryModel
from auto_slopp.openproject.openapi_client.models.query_update_form import QueryUpdateForm
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
    api_instance = auto_slopp.openproject.openapi_client.QueriesApi(api_client)
    id = 1 # int | Query id
    query_update_form = auto_slopp.openproject.openapi_client.QueryUpdateForm() # QueryUpdateForm |  (optional)

    try:
        # Edit Query
        api_response = api_instance.edit_query(id, query_update_form=query_update_form)
        print("The response of QueriesApi->edit_query:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling QueriesApi->edit_query: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Query id | 
 **query_update_form** | [**QueryUpdateForm**](QueryUpdateForm.md)|  | [optional] 

### Return type

[**QueryModel**](QueryModel.md)

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
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** edit work package |  -  |
**404** | Returned if the query does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view work packages in the query&#39;s project (unless global) |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |
**422** | Returned if:  * the client tries to modify a read-only property (&#x60;PropertyIsReadOnly&#x60;)  * a constraint for a property was violated (&#x60;PropertyConstraintViolation&#x60;)  * the client provides a link to an invalid resource (&#x60;ResourceTypeMismatch&#x60;) |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_queries**
> object list_queries(filters=filters)

List queries

Returns a collection of queries. The collection can be filtered via query parameters similar to how work packages are filtered. Please note however, that the filters are applied to the queries and not to the work packages the queries in turn might return.

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
    api_instance = auto_slopp.openproject.openapi_client.QueriesApi(api_client)
    filters = '[{ \"project_id\": { \"operator\": \"!*\", \"values\": null }\" }]' # str | JSON specifying filter conditions. Currently supported filters are:  + project: filters queries by the project they are assigned to. If the project filter is passed with the `!*` (not any) operator, global queries are returned.  + id: filters queries based on their id  + updated_at: filters queries based on the last time they where updated (optional)

    try:
        # List queries
        api_response = api_instance.list_queries(filters=filters)
        print("The response of QueriesApi->list_queries:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling QueriesApi->list_queries: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **filters** | **str**| JSON specifying filter conditions. Currently supported filters are:  + project: filters queries by the project they are assigned to. If the project filter is passed with the &#x60;!*&#x60; (not any) operator, global queries are returned.  + id: filters queries based on their id  + updated_at: filters queries based on the last time they where updated | [optional] 

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
**403** | Returned if the client does not have sufficient permissions to see queries.  **Required permission:** view work packages or manage public queries in any project |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **query_create_form**
> query_create_form(query_create_form=query_create_form)

Query Create Form



### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.query_create_form import QueryCreateForm
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
    api_instance = auto_slopp.openproject.openapi_client.QueriesApi(api_client)
    query_create_form = auto_slopp.openproject.openapi_client.QueryCreateForm() # QueryCreateForm |  (optional)

    try:
        # Query Create Form
        api_instance.query_create_form(query_create_form=query_create_form)
    except Exception as e:
        print("Exception when calling QueriesApi->query_create_form: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **query_create_form** | [**QueryCreateForm**](QueryCreateForm.md)|  | [optional] 

### Return type

void (empty response body)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: Not defined

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **query_update_form**
> query_update_form(id, query_update_form=query_update_form)

Query Update Form



### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.query_update_form import QueryUpdateForm
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
    api_instance = auto_slopp.openproject.openapi_client.QueriesApi(api_client)
    id = 1 # int | Query id
    query_update_form = auto_slopp.openproject.openapi_client.QueryUpdateForm() # QueryUpdateForm |  (optional)

    try:
        # Query Update Form
        api_instance.query_update_form(id, query_update_form=query_update_form)
    except Exception as e:
        print("Exception when calling QueriesApi->query_update_form: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Query id | 
 **query_update_form** | [**QueryUpdateForm**](QueryUpdateForm.md)|  | [optional] 

### Return type

void (empty response body)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: Not defined

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **star_query**
> object star_query(id)

Star query



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
    api_instance = auto_slopp.openproject.openapi_client.QueriesApi(api_client)
    id = 1 # int | Query id

    try:
        # Star query
        api_response = api_instance.star_query(id)
        print("The response of QueriesApi->star_query:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling QueriesApi->star_query: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Query id | 

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
**400** | Occurs when the client did not send a valid JSON object in the request body. |  -  |
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** for own queries none; for public queries: manage public queries  *Note that you will only receive this error, if you are at least allowed to see the corresponding query.* |  -  |
**404** | Returned if the query does not exist or the client does not have sufficient permissions to see it.  **Required condition:** query belongs to user or query is public  **Required permission:** view work package in queries project |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **unstar_query**
> object unstar_query(id)

Unstar query



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
    api_instance = auto_slopp.openproject.openapi_client.QueriesApi(api_client)
    id = 1 # int | Query id

    try:
        # Unstar query
        api_response = api_instance.unstar_query(id)
        print("The response of QueriesApi->unstar_query:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling QueriesApi->unstar_query: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Query id | 

### Return type

**object**

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json, text/plain

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**400** | Occurs when the client did not send a valid JSON object in the request body. |  -  |
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** for own queries none; for public queries: manage public queries  *Note that you will only receive this error, if you are at least allowed to see the corresponding query.* |  -  |
**404** | Returned if the query does not exist or the client does not have sufficient permissions to see it.  **Required condition:** query belongs to user or query is public  **Required permission:** view work package in queries project |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **view_default_query**
> object view_default_query(filters=filters, offset=offset, page_size=page_size, sort_by=sort_by, group_by=group_by, show_sums=show_sums, timestamps=timestamps, timeline_visible=timeline_visible, timeline_zoom_level=timeline_zoom_level, show_hierarchies=show_hierarchies)

View default query

Same as [viewing an existing, persisted Query](https://www.openproject.org/docs/api/endpoints/queries/#list-queries) in its response, this resource returns an unpersisted query and by that allows to get the default query configuration. The client may also provide additional parameters which will modify the default query.

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
    api_instance = auto_slopp.openproject.openapi_client.QueriesApi(api_client)
    filters = '[{ "status_id": { "operator": "o", "values": null }}]' # str | JSON specifying filter conditions. The filters provided as parameters are not applied to the query but are instead used to override the query's persisted filters. All filters also accepted by the work packages endpoint are accepted. If no filter is to be applied, the client should send an empty array (`[]`). (optional) (default to '[{ "status_id": { "operator": "o", "values": null }}]')
    offset = 1 # int | Page number inside the queries' result collection of work packages. (optional) (default to 1)
    page_size = 25 # int | Number of elements to display per page for the queries' result collection of work packages. (optional)
    sort_by = '[["id", "asc"]]' # str | JSON specifying sort criteria. The sort criteria is applied to the query's result collection of work packages overriding the query's persisted sort criteria. (optional) (default to '[["id", "asc"]]')
    group_by = 'status' # str | The column to group by. The grouping criteria is applied to the to the query's result collection of work packages overriding the query's persisted group criteria. (optional)
    show_sums = False # bool | Indicates whether properties should be summed up if they support it. The showSums parameter is applied to the to the query's result collection of work packages overriding the query's persisted sums property. (optional) (default to False)
    timestamps = 'PT0S' # str | Indicates the timestamps to filter by when showing changed attributes on work packages. Values can be either ISO8601 dates, ISO8601 durations and the following relative date keywords: \"oneDayAgo@HH:MM+HH:MM\", \"lastWorkingDay@HH:MM+HH:MM\", \"oneWeekAgo@HH:MM+HH:MM\", \"oneMonthAgo@HH:MM+HH:MM\". The first \"HH:MM\" part represents the zero paded hours and minutes. The last \"+HH:MM\" part represents the timezone offset from UTC associated with the time, the offset can be positive or negative e.g.\"oneDayAgo@01:00+01:00\", \"oneDayAgo@01:00-01:00\". Values older than 1 day are accepted only with valid Enterprise Token available.  (optional) (default to 'PT0S')
    timeline_visible = False # bool | Indicates whether the timeline should be shown. (optional) (default to False)
    timeline_zoom_level = 'days' # str | Indicates in what zoom level the timeline should be shown. Valid values are  `days`, `weeks`, `months`, `quarters`, and `years`. (optional) (default to 'days')
    show_hierarchies = True # bool | Indicates whether the hierarchy mode should be enabled. (optional) (default to True)

    try:
        # View default query
        api_response = api_instance.view_default_query(filters=filters, offset=offset, page_size=page_size, sort_by=sort_by, group_by=group_by, show_sums=show_sums, timestamps=timestamps, timeline_visible=timeline_visible, timeline_zoom_level=timeline_zoom_level, show_hierarchies=show_hierarchies)
        print("The response of QueriesApi->view_default_query:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling QueriesApi->view_default_query: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **filters** | **str**| JSON specifying filter conditions. The filters provided as parameters are not applied to the query but are instead used to override the query&#39;s persisted filters. All filters also accepted by the work packages endpoint are accepted. If no filter is to be applied, the client should send an empty array (&#x60;[]&#x60;). | [optional] [default to &#39;[{ &quot;status_id&quot;: { &quot;operator&quot;: &quot;o&quot;, &quot;values&quot;: null }}]&#39;]
 **offset** | **int**| Page number inside the queries&#39; result collection of work packages. | [optional] [default to 1]
 **page_size** | **int**| Number of elements to display per page for the queries&#39; result collection of work packages. | [optional] 
 **sort_by** | **str**| JSON specifying sort criteria. The sort criteria is applied to the query&#39;s result collection of work packages overriding the query&#39;s persisted sort criteria. | [optional] [default to &#39;[[&quot;id&quot;, &quot;asc&quot;]]&#39;]
 **group_by** | **str**| The column to group by. The grouping criteria is applied to the to the query&#39;s result collection of work packages overriding the query&#39;s persisted group criteria. | [optional] 
 **show_sums** | **bool**| Indicates whether properties should be summed up if they support it. The showSums parameter is applied to the to the query&#39;s result collection of work packages overriding the query&#39;s persisted sums property. | [optional] [default to False]
 **timestamps** | **str**| Indicates the timestamps to filter by when showing changed attributes on work packages. Values can be either ISO8601 dates, ISO8601 durations and the following relative date keywords: \&quot;oneDayAgo@HH:MM+HH:MM\&quot;, \&quot;lastWorkingDay@HH:MM+HH:MM\&quot;, \&quot;oneWeekAgo@HH:MM+HH:MM\&quot;, \&quot;oneMonthAgo@HH:MM+HH:MM\&quot;. The first \&quot;HH:MM\&quot; part represents the zero paded hours and minutes. The last \&quot;+HH:MM\&quot; part represents the timezone offset from UTC associated with the time, the offset can be positive or negative e.g.\&quot;oneDayAgo@01:00+01:00\&quot;, \&quot;oneDayAgo@01:00-01:00\&quot;. Values older than 1 day are accepted only with valid Enterprise Token available.  | [optional] [default to &#39;PT0S&#39;]
 **timeline_visible** | **bool**| Indicates whether the timeline should be shown. | [optional] [default to False]
 **timeline_zoom_level** | **str**| Indicates in what zoom level the timeline should be shown. Valid values are  &#x60;days&#x60;, &#x60;weeks&#x60;, &#x60;months&#x60;, &#x60;quarters&#x60;, and &#x60;years&#x60;. | [optional] [default to &#39;days&#39;]
 **show_hierarchies** | **bool**| Indicates whether the hierarchy mode should be enabled. | [optional] [default to True]

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
**403** | Returned if the client does not have sufficient permissions to see the default query.  **Required permission:** view work packages in any project |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **view_default_query_for_project**
> object view_default_query_for_project(id, filters=filters, offset=offset, page_size=page_size, sort_by=sort_by, group_by=group_by, show_sums=show_sums, timestamps=timestamps, timeline_visible=timeline_visible, show_hierarchies=show_hierarchies)

View default query for project

Same as [viewing an existing, persisted Query](https://www.openproject.org/docs/api/endpoints/queries/#list-queries)
in its response, this resource returns an unpersisted query and by that allows
to get the default query configuration. The client may also provide additional
parameters which will modify the default query. The query will already be scoped
to the project.

This endpoint is deprecated and replaced by [`/api/v3/workspaces/{id}/queries/default`](https://www.openproject.org/docs/api/endpoints/queries/#view-default-query-for-workspace)

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
    api_instance = auto_slopp.openproject.openapi_client.QueriesApi(api_client)
    id = 1 # int | Id of the project the default query is requested for
    filters = '[{ "status_id": { "operator": "o", "values": null }}]' # str | JSON specifying filter conditions. The filters provided as parameters are not applied to the query but are instead used to override the query's persisted filters. All filters also accepted by the work packages endpoint are accepted. If no filter is to be applied, the client should send an empty array (`[]`). (optional) (default to '[{ "status_id": { "operator": "o", "values": null }}]')
    offset = 1 # int | Page number inside the queries' result collection of work packages. (optional) (default to 1)
    page_size = 25 # int | Number of elements to display per page for the queries' result collection of work packages. (optional)
    sort_by = '[["id", "asc"]]' # str | JSON specifying sort criteria. The sort criteria is applied to the query's result collection of work packages overriding the query's persisted sort criteria. (optional) (default to '[["id", "asc"]]')
    group_by = 'status' # str | The column to group by. The grouping criteria is applied to the to the query's result collection of work packages overriding the query's persisted group criteria. (optional)
    show_sums = False # bool | Indicates whether properties should be summed up if they support it. The showSums parameter is applied to the to the query's result collection of work packages overriding the query's persisted sums property. (optional) (default to False)
    timestamps = 'PT0S' # str | Indicates the timestamps to filter by when showing changed attributes on work packages. Values can be either ISO8601 dates, ISO8601 durations and the following relative date keywords: \"oneDayAgo@HH:MM+HH:MM\", \"lastWorkingDay@HH:MM+HH:MM\", \"oneWeekAgo@HH:MM+HH:MM\", \"oneMonthAgo@HH:MM+HH:MM\". The first \"HH:MM\" part represents the zero paded hours and minutes. The last \"+HH:MM\" part represents the timezone offset from UTC associated with the time. Values older than 1 day are accepted only with valid Enterprise Token available.  (optional) (default to 'PT0S')
    timeline_visible = False # bool | Indicates whether the timeline should be shown. (optional) (default to False)
    show_hierarchies = True # bool | Indicates whether the hierarchy mode should be enabled. (optional) (default to True)

    try:
        # View default query for project
        api_response = api_instance.view_default_query_for_project(id, filters=filters, offset=offset, page_size=page_size, sort_by=sort_by, group_by=group_by, show_sums=show_sums, timestamps=timestamps, timeline_visible=timeline_visible, show_hierarchies=show_hierarchies)
        print("The response of QueriesApi->view_default_query_for_project:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling QueriesApi->view_default_query_for_project: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Id of the project the default query is requested for | 
 **filters** | **str**| JSON specifying filter conditions. The filters provided as parameters are not applied to the query but are instead used to override the query&#39;s persisted filters. All filters also accepted by the work packages endpoint are accepted. If no filter is to be applied, the client should send an empty array (&#x60;[]&#x60;). | [optional] [default to &#39;[{ &quot;status_id&quot;: { &quot;operator&quot;: &quot;o&quot;, &quot;values&quot;: null }}]&#39;]
 **offset** | **int**| Page number inside the queries&#39; result collection of work packages. | [optional] [default to 1]
 **page_size** | **int**| Number of elements to display per page for the queries&#39; result collection of work packages. | [optional] 
 **sort_by** | **str**| JSON specifying sort criteria. The sort criteria is applied to the query&#39;s result collection of work packages overriding the query&#39;s persisted sort criteria. | [optional] [default to &#39;[[&quot;id&quot;, &quot;asc&quot;]]&#39;]
 **group_by** | **str**| The column to group by. The grouping criteria is applied to the to the query&#39;s result collection of work packages overriding the query&#39;s persisted group criteria. | [optional] 
 **show_sums** | **bool**| Indicates whether properties should be summed up if they support it. The showSums parameter is applied to the to the query&#39;s result collection of work packages overriding the query&#39;s persisted sums property. | [optional] [default to False]
 **timestamps** | **str**| Indicates the timestamps to filter by when showing changed attributes on work packages. Values can be either ISO8601 dates, ISO8601 durations and the following relative date keywords: \&quot;oneDayAgo@HH:MM+HH:MM\&quot;, \&quot;lastWorkingDay@HH:MM+HH:MM\&quot;, \&quot;oneWeekAgo@HH:MM+HH:MM\&quot;, \&quot;oneMonthAgo@HH:MM+HH:MM\&quot;. The first \&quot;HH:MM\&quot; part represents the zero paded hours and minutes. The last \&quot;+HH:MM\&quot; part represents the timezone offset from UTC associated with the time. Values older than 1 day are accepted only with valid Enterprise Token available.  | [optional] [default to &#39;PT0S&#39;]
 **timeline_visible** | **bool**| Indicates whether the timeline should be shown. | [optional] [default to False]
 **show_hierarchies** | **bool**| Indicates whether the hierarchy mode should be enabled. | [optional] [default to True]

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
**403** | Returned if the client does not have sufficient permissions to see the default query.  **Required permission:** view work packages in the project |  -  |
**404** | Returned if the client does not have sufficient permissions to see the project.  **Required permission:** any permission in the project |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **view_default_query_for_workspace**
> object view_default_query_for_workspace(id, filters=filters, offset=offset, page_size=page_size, sort_by=sort_by, group_by=group_by, show_sums=show_sums, timestamps=timestamps, timeline_visible=timeline_visible, show_hierarchies=show_hierarchies)

View default query for workspace

Same as [viewing an existing, persisted Query](https://www.openproject.org/docs/api/endpoints/queries/#list-queries) in its response, this resource returns an unpersisted query and by that allows to get the default query configuration. The client may also provide additional parameters which will modify the default query. The query will already be scoped to the workspace.

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
    api_instance = auto_slopp.openproject.openapi_client.QueriesApi(api_client)
    id = 1 # int | Id of the workspace the default query is requested for
    filters = '[{ "status_id": { "operator": "o", "values": null }}]' # str | JSON specifying filter conditions. The filters provided as parameters are not applied to the query but are instead used to override the query's persisted filters. All filters also accepted by the work packages endpoint are accepted. If no filter is to be applied, the client should send an empty array (`[]`). (optional) (default to '[{ "status_id": { "operator": "o", "values": null }}]')
    offset = 1 # int | Page number inside the queries' result collection of work packages. (optional) (default to 1)
    page_size = 25 # int | Number of elements to display per page for the queries' result collection of work packages. (optional)
    sort_by = '[["id", "asc"]]' # str | JSON specifying sort criteria. The sort criteria is applied to the query's result collection of work packages overriding the query's persisted sort criteria. (optional) (default to '[["id", "asc"]]')
    group_by = 'status' # str | The column to group by. The grouping criteria is applied to the to the query's result collection of work packages overriding the query's persisted group criteria. (optional)
    show_sums = False # bool | Indicates whether properties should be summed up if they support it. The showSums parameter is applied to the to the query's result collection of work packages overriding the query's persisted sums property. (optional) (default to False)
    timestamps = 'PT0S' # str | Indicates the timestamps to filter by when showing changed attributes on work packages. Values can be either ISO8601 dates, ISO8601 durations and the following relative date keywords: \"oneDayAgo@HH:MM+HH:MM\", \"lastWorkingDay@HH:MM+HH:MM\", \"oneWeekAgo@HH:MM+HH:MM\", \"oneMonthAgo@HH:MM+HH:MM\". The first \"HH:MM\" part represents the zero paded hours and minutes. The last \"+HH:MM\" part represents the timezone offset from UTC associated with the time. Values older than 1 day are accepted only with valid Enterprise Token available.  (optional) (default to 'PT0S')
    timeline_visible = False # bool | Indicates whether the timeline should be shown. (optional) (default to False)
    show_hierarchies = True # bool | Indicates whether the hierarchy mode should be enabled. (optional) (default to True)

    try:
        # View default query for workspace
        api_response = api_instance.view_default_query_for_workspace(id, filters=filters, offset=offset, page_size=page_size, sort_by=sort_by, group_by=group_by, show_sums=show_sums, timestamps=timestamps, timeline_visible=timeline_visible, show_hierarchies=show_hierarchies)
        print("The response of QueriesApi->view_default_query_for_workspace:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling QueriesApi->view_default_query_for_workspace: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Id of the workspace the default query is requested for | 
 **filters** | **str**| JSON specifying filter conditions. The filters provided as parameters are not applied to the query but are instead used to override the query&#39;s persisted filters. All filters also accepted by the work packages endpoint are accepted. If no filter is to be applied, the client should send an empty array (&#x60;[]&#x60;). | [optional] [default to &#39;[{ &quot;status_id&quot;: { &quot;operator&quot;: &quot;o&quot;, &quot;values&quot;: null }}]&#39;]
 **offset** | **int**| Page number inside the queries&#39; result collection of work packages. | [optional] [default to 1]
 **page_size** | **int**| Number of elements to display per page for the queries&#39; result collection of work packages. | [optional] 
 **sort_by** | **str**| JSON specifying sort criteria. The sort criteria is applied to the query&#39;s result collection of work packages overriding the query&#39;s persisted sort criteria. | [optional] [default to &#39;[[&quot;id&quot;, &quot;asc&quot;]]&#39;]
 **group_by** | **str**| The column to group by. The grouping criteria is applied to the to the query&#39;s result collection of work packages overriding the query&#39;s persisted group criteria. | [optional] 
 **show_sums** | **bool**| Indicates whether properties should be summed up if they support it. The showSums parameter is applied to the to the query&#39;s result collection of work packages overriding the query&#39;s persisted sums property. | [optional] [default to False]
 **timestamps** | **str**| Indicates the timestamps to filter by when showing changed attributes on work packages. Values can be either ISO8601 dates, ISO8601 durations and the following relative date keywords: \&quot;oneDayAgo@HH:MM+HH:MM\&quot;, \&quot;lastWorkingDay@HH:MM+HH:MM\&quot;, \&quot;oneWeekAgo@HH:MM+HH:MM\&quot;, \&quot;oneMonthAgo@HH:MM+HH:MM\&quot;. The first \&quot;HH:MM\&quot; part represents the zero paded hours and minutes. The last \&quot;+HH:MM\&quot; part represents the timezone offset from UTC associated with the time. Values older than 1 day are accepted only with valid Enterprise Token available.  | [optional] [default to &#39;PT0S&#39;]
 **timeline_visible** | **bool**| Indicates whether the timeline should be shown. | [optional] [default to False]
 **show_hierarchies** | **bool**| Indicates whether the hierarchy mode should be enabled. | [optional] [default to True]

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
**403** | Returned if the client does not have sufficient permissions to see the default query.  **Required permission:** view work packages in the workspace |  -  |
**404** | Returned if the client does not have sufficient permissions to see the workspace.  **Required permission:** any permission in the workspace |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **view_query**
> QueryModel view_query(id, filters=filters, offset=offset, page_size=page_size, columns=columns, sort_by=sort_by, group_by=group_by, show_sums=show_sums, timestamps=timestamps, timeline_visible=timeline_visible, timeline_labels=timeline_labels, highlighting_mode=highlighting_mode, highlighted_attributes=highlighted_attributes, show_hierarchies=show_hierarchies)

View query

Retrieve an individual query as identified by the id parameter. Then endpoint accepts a number of parameters that can be used to override the resources' persisted parameters.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.query_model import QueryModel
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
    api_instance = auto_slopp.openproject.openapi_client.QueriesApi(api_client)
    id = 1 # int | Query id
    filters = '[{ "status_id": { "operator": "o", "values": null }}]' # str | JSON specifying filter conditions. The filters provided as parameters are not applied to the query but are instead used to override the query's persisted filters. All filters also accepted by the work packages endpoint are accepted. If no filter is to be applied, the client should send an empty array (`[]`). (optional) (default to '[{ "status_id": { "operator": "o", "values": null }}]')
    offset = 1 # int | Page number inside the queries' result collection of work packages. (optional) (default to 1)
    page_size = 25 # int | Number of elements to display per page for the queries' result collection of work packages. (optional)
    columns = '[\'type\', \'priority\']' # str | Selected columns for the table view. (optional) (default to '[\'type\', \'priority\']')
    sort_by = '[["id", "asc"]]' # str | JSON specifying sort criteria. The sort criteria is applied to the query's result collection of work packages overriding the query's persisted sort criteria. (optional) (default to '[["id", "asc"]]')
    group_by = 'status' # str | The column to group by. The grouping criteria is applied to the to the query's result collection of work packages overriding the query's persisted group criteria. (optional)
    show_sums = False # bool | Indicates whether properties should be summed up if they support it. The showSums parameter is applied to the to the query's result collection of work packages overriding the query's persisted sums property. (optional) (default to False)
    timestamps = 'PT0S' # str | Indicates the timestamps to filter by when showing changed attributes on work packages. Values can be either ISO8601 dates, ISO8601 durations and the following relative date keywords: \"oneDayAgo@HH:MM+HH:MM\", \"lastWorkingDay@HH:MM+HH:MM\", \"oneWeekAgo@HH:MM+HH:MM\", \"oneMonthAgo@HH:MM+HH:MM\". The first \"HH:MM\" part represents the zero paded hours and minutes. The last \"+HH:MM\" part represents the timezone offset from UTC associated with the time, the offset can be positive or negative e.g.\"oneDayAgo@01:00+01:00\", \"oneDayAgo@01:00-01:00\". Values older than 1 day are accepted only with valid Enterprise Token available.  (optional) (default to 'PT0S')
    timeline_visible = False # bool | Indicates whether the timeline should be shown. (optional) (default to False)
    timeline_labels = '{}' # str | Overridden labels in the timeline view (optional) (default to '{}')
    highlighting_mode = 'inline' # str | Highlighting mode for the table view. (optional) (default to 'inline')
    highlighted_attributes = '[\'type\', \'priority\']' # str | Highlighted attributes mode for the table view when `highlightingMode` is `inline`. When set to `[]` all highlightable attributes will be returned as `highlightedAttributes`. (optional) (default to '[\'type\', \'priority\']')
    show_hierarchies = True # bool | Indicates whether the hierarchy mode should be enabled. (optional) (default to True)

    try:
        # View query
        api_response = api_instance.view_query(id, filters=filters, offset=offset, page_size=page_size, columns=columns, sort_by=sort_by, group_by=group_by, show_sums=show_sums, timestamps=timestamps, timeline_visible=timeline_visible, timeline_labels=timeline_labels, highlighting_mode=highlighting_mode, highlighted_attributes=highlighted_attributes, show_hierarchies=show_hierarchies)
        print("The response of QueriesApi->view_query:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling QueriesApi->view_query: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Query id | 
 **filters** | **str**| JSON specifying filter conditions. The filters provided as parameters are not applied to the query but are instead used to override the query&#39;s persisted filters. All filters also accepted by the work packages endpoint are accepted. If no filter is to be applied, the client should send an empty array (&#x60;[]&#x60;). | [optional] [default to &#39;[{ &quot;status_id&quot;: { &quot;operator&quot;: &quot;o&quot;, &quot;values&quot;: null }}]&#39;]
 **offset** | **int**| Page number inside the queries&#39; result collection of work packages. | [optional] [default to 1]
 **page_size** | **int**| Number of elements to display per page for the queries&#39; result collection of work packages. | [optional] 
 **columns** | **str**| Selected columns for the table view. | [optional] [default to &#39;[\&#39;type\&#39;, \&#39;priority\&#39;]&#39;]
 **sort_by** | **str**| JSON specifying sort criteria. The sort criteria is applied to the query&#39;s result collection of work packages overriding the query&#39;s persisted sort criteria. | [optional] [default to &#39;[[&quot;id&quot;, &quot;asc&quot;]]&#39;]
 **group_by** | **str**| The column to group by. The grouping criteria is applied to the to the query&#39;s result collection of work packages overriding the query&#39;s persisted group criteria. | [optional] 
 **show_sums** | **bool**| Indicates whether properties should be summed up if they support it. The showSums parameter is applied to the to the query&#39;s result collection of work packages overriding the query&#39;s persisted sums property. | [optional] [default to False]
 **timestamps** | **str**| Indicates the timestamps to filter by when showing changed attributes on work packages. Values can be either ISO8601 dates, ISO8601 durations and the following relative date keywords: \&quot;oneDayAgo@HH:MM+HH:MM\&quot;, \&quot;lastWorkingDay@HH:MM+HH:MM\&quot;, \&quot;oneWeekAgo@HH:MM+HH:MM\&quot;, \&quot;oneMonthAgo@HH:MM+HH:MM\&quot;. The first \&quot;HH:MM\&quot; part represents the zero paded hours and minutes. The last \&quot;+HH:MM\&quot; part represents the timezone offset from UTC associated with the time, the offset can be positive or negative e.g.\&quot;oneDayAgo@01:00+01:00\&quot;, \&quot;oneDayAgo@01:00-01:00\&quot;. Values older than 1 day are accepted only with valid Enterprise Token available.  | [optional] [default to &#39;PT0S&#39;]
 **timeline_visible** | **bool**| Indicates whether the timeline should be shown. | [optional] [default to False]
 **timeline_labels** | **str**| Overridden labels in the timeline view | [optional] [default to &#39;{}&#39;]
 **highlighting_mode** | **str**| Highlighting mode for the table view. | [optional] [default to &#39;inline&#39;]
 **highlighted_attributes** | **str**| Highlighted attributes mode for the table view when &#x60;highlightingMode&#x60; is &#x60;inline&#x60;. When set to &#x60;[]&#x60; all highlightable attributes will be returned as &#x60;highlightedAttributes&#x60;. | [optional] [default to &#39;[\&#39;type\&#39;, \&#39;priority\&#39;]&#39;]
 **show_hierarchies** | **bool**| Indicates whether the hierarchy mode should be enabled. | [optional] [default to True]

### Return type

[**QueryModel**](QueryModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**404** | Returned if the query does not exist or the client does not have sufficient permissions to see it.  **Required condition:** query belongs to user or query is public  **Required permission:** view work package in queries project |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **view_schema_for_global_queries**
> object view_schema_for_global_queries()

View schema for global queries

Retrieve the schema for global queries, those, that are not assigned to a project.

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
    api_instance = auto_slopp.openproject.openapi_client.QueriesApi(api_client)

    try:
        # View schema for global queries
        api_response = api_instance.view_schema_for_global_queries()
        print("The response of QueriesApi->view_schema_for_global_queries:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling QueriesApi->view_schema_for_global_queries: %s\n" % e)
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
**403** | **Required permission:** view work package in any project |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **view_schema_for_project_queries**
> object view_schema_for_project_queries(id)

View schema for project queries

Retrieve the schema for project queries.

This endpoint is deprecated and replaced by ['/api/v3/workspaces/{id}/queries/schema`](https://www.openproject.org/docs/api/endpoints/queries/#view-schema-for-workspace-queries)

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
    api_instance = auto_slopp.openproject.openapi_client.QueriesApi(api_client)
    id = 1 # int | Project id

    try:
        # View schema for project queries
        api_response = api_instance.view_schema_for_project_queries(id)
        print("The response of QueriesApi->view_schema_for_project_queries:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling QueriesApi->view_schema_for_project_queries: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Project id | 

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
**403** | **Required permission:** view work package in the project |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **view_schema_for_workspace_queries**
> object view_schema_for_workspace_queries(id)

View schema for workspace queries

Retrieve the schema for workspace queries.

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
    api_instance = auto_slopp.openproject.openapi_client.QueriesApi(api_client)
    id = 1 # int | Project id

    try:
        # View schema for workspace queries
        api_response = api_instance.view_schema_for_workspace_queries(id)
        print("The response of QueriesApi->view_schema_for_workspace_queries:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling QueriesApi->view_schema_for_workspace_queries: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Project id | 

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
**403** | **Required permission:** view work package in the workspace |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

