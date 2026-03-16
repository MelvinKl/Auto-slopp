# openproject_client.GridsApi

All URIs are relative to *https://openproject.melvin.beer*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_grid**](GridsApi.md#create_grid) | **POST** /api/v3/grids | Create a grid
[**get_grid**](GridsApi.md#get_grid) | **GET** /api/v3/grids/{id} | Get a grid
[**grid_create_form**](GridsApi.md#grid_create_form) | **POST** /api/v3/grids/form | Grid Create Form
[**grid_update_form**](GridsApi.md#grid_update_form) | **POST** /api/v3/grids/{id}/form | Grid Update Form
[**list_grids**](GridsApi.md#list_grids) | **GET** /api/v3/grids | List grids
[**update_grid**](GridsApi.md#update_grid) | **PATCH** /api/v3/grids/{id} | Update a grid


# **create_grid**
> GridReadModel create_grid(grid_write_model=grid_write_model)

Create a grid

Creates a new grid applying the attributes provided in the body. The constraints applied to the grid depend on the
page the grid is placed in which is why the create form endpoint should be used to be guided when wanting to
create a grid.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.grid_read_model import GridReadModel
from openproject_client.models.grid_write_model import GridWriteModel
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
    api_instance = openproject_client.GridsApi(api_client)
    grid_write_model = openproject_client.GridWriteModel() # GridWriteModel |  (optional)

    try:
        # Create a grid
        api_response = api_instance.create_grid(grid_write_model=grid_write_model)
        print("The response of GridsApi->create_grid:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling GridsApi->create_grid: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **grid_write_model** | [**GridWriteModel**](GridWriteModel.md)|  | [optional] 

### Return type

[**GridReadModel**](GridReadModel.md)

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
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** Depends on the page the grid is defined for. |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |
**422** | Returned if:  * a constraint for a property was violated (&#x60;PropertyConstraintViolation&#x60;) |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_grid**
> GridReadModel get_grid(id)

Get a grid

Fetches a single grid identified by its id.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.grid_read_model import GridReadModel
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
    api_instance = openproject_client.GridsApi(api_client)
    id = 42 # int | Grid id

    try:
        # Get a grid
        api_response = api_instance.get_grid(id)
        print("The response of GridsApi->get_grid:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling GridsApi->get_grid: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Grid id | 

### Return type

[**GridReadModel**](GridReadModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**404** | Returned if the Grid does not exist or if the user does not have permission to view it.  **Required permission** depends on the page the grid is defined for |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **grid_create_form**
> grid_create_form()

Grid Create Form



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
    api_instance = openproject_client.GridsApi(api_client)

    try:
        # Grid Create Form
        api_instance.grid_create_form()
    except Exception as e:
        print("Exception when calling GridsApi->grid_create_form: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **grid_update_form**
> object grid_update_form(id)

Grid Update Form



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
    api_instance = openproject_client.GridsApi(api_client)
    id = 1 # int | ID of the grid being modified

    try:
        # Grid Update Form
        api_response = api_instance.grid_update_form(id)
        print("The response of GridsApi->grid_update_form:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling GridsApi->grid_update_form: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| ID of the grid being modified | 

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
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** depends on the page the grid is defined for.  *Note that you will only receive this error, if you are at least allowed to see the corresponding grid.* |  -  |
**404** | Returned if the grid does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view work package |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_grids**
> GridCollectionModel list_grids(offset=offset, page_size=page_size, filters=filters)

List grids

Lists all grids matching the provided filters and being part of the selected query page. The grids returned will
also depend on the permissions of the requesting user.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.grid_collection_model import GridCollectionModel
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
    api_instance = openproject_client.GridsApi(api_client)
    offset = 1 # int | Page number inside the requested collection. (optional) (default to 1)
    page_size = 30 # int | Number of elements to display per page. (optional) (default to 30)
    filters = '[{ \"page\": { \"operator\": \"=\", \"values\": [\"/my/page\"] } }]' # str | JSON specifying filter conditions. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported filters are:  - page: Filter grid by work package (optional)

    try:
        # List grids
        api_response = api_instance.list_grids(offset=offset, page_size=page_size, filters=filters)
        print("The response of GridsApi->list_grids:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling GridsApi->list_grids: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **offset** | **int**| Page number inside the requested collection. | [optional] [default to 1]
 **page_size** | **int**| Number of elements to display per page. | [optional] [default to 30]
 **filters** | **str**| JSON specifying filter conditions. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported filters are:  - page: Filter grid by work package | [optional] 

### Return type

[**GridCollectionModel**](GridCollectionModel.md)

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
**403** | Returned if the client is not logged in and login is required. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_grid**
> GridReadModel update_grid(id, grid_write_model=grid_write_model)

Update a grid

Updates the given grid by applying the attributes provided in the body. The constraints applied to the grid depend
on the page the grid is placed in which is why the create form endpoint should be used to be guided when wanting
to update a grid.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.grid_read_model import GridReadModel
from openproject_client.models.grid_write_model import GridWriteModel
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
    api_instance = openproject_client.GridsApi(api_client)
    id = 42 # int | Grid id
    grid_write_model = openproject_client.GridWriteModel() # GridWriteModel |  (optional)

    try:
        # Update a grid
        api_response = api_instance.update_grid(id, grid_write_model=grid_write_model)
        print("The response of GridsApi->update_grid:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling GridsApi->update_grid: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Grid id | 
 **grid_write_model** | [**GridWriteModel**](GridWriteModel.md)|  | [optional] 

### Return type

[**GridReadModel**](GridReadModel.md)

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
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** The permission depends on the page the grid is placed in. |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |
**422** | Returned if:  * a constraint for a property was violated (&#x60;PropertyConstraintViolation&#x60;) |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

