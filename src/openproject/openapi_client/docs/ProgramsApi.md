# openproject_client.ProgramsApi

All URIs are relative to *https://openproject.melvin.beer*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_program**](ProgramsApi.md#delete_program) | **DELETE** /api/v3/programs/{id} | Delete Program
[**list_programs**](ProgramsApi.md#list_programs) | **GET** /api/v3/programs | List programs
[**program_update_form**](ProgramsApi.md#program_update_form) | **POST** /api/v3/programs/{id}/form | Program update form
[**update_program**](ProgramsApi.md#update_program) | **PATCH** /api/v3/programs/{id} | Update Program
[**view_program**](ProgramsApi.md#view_program) | **GET** /api/v3/programs/{id} | View program


# **delete_program**
> delete_program(id)

Delete Program

Deletes the program permanently. As this is a lengthy process, the actual deletion is carried out asynchronously.
So the program might exist well after the request has returned successfully. To prevent unwanted changes to
the program scheduled for deletion, it is archived at once.

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
    api_instance = openproject_client.ProgramsApi(api_client)
    id = 1 # int | Program id

    try:
        # Delete Program
        api_instance.delete_program(id)
    except Exception as e:
        print("Exception when calling ProgramsApi->delete_program: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Program id | 

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
**204** | Returned if the program was successfully deleted. There is currently no endpoint to query for the actual deletion status. Such an endpoint _might_ be added in the future. |  -  |
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** admin |  -  |
**404** | Returned if the program does not exist or the client does not have sufficient permissions to see it.  **Required permission:** any permission in the program  *Note: A client without sufficient permissions shall not be able to test for the existence of a version. That&#39;s why a 404 is returned here, even if a 403 might be more appropriate.* |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |
**422** | Returned if the program cannot be deleted. This can happen when there are still references to the program in other workspaces that need to be severed at first. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_programs**
> ProgramCollectionModel list_programs(filters=filters, sort_by=sort_by, select=select)

List programs

Returns a collection of programs. The collection can be filtered via query parameters similar to how work packages are filtered. In addition to the provided filter, the result set is always limited to only contain programs the client is allowed to see.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.program_collection_model import ProgramCollectionModel
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
    api_instance = openproject_client.ProgramsApi(api_client)
    filters = '[{ \"ancestor\": { \"operator\": \"=\", \"values\": [\"1\"] }\" }]' # str | JSON specifying filter conditions. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported filters are:  + active: based on the active property of the program + ancestor: filters programs by their ancestor. A program is not considered to be its own ancestor. + available_project_attributes: filters programs based on the activated project attributes. + created_at: based on the time the program was created + favorited: based on the favorited property of the program + id: based on programs' id. + latest_activity_at: based on the time the last activity was registered on a program. + name_and_identifier: based on both the name and the identifier. + parent_id: filters programs by their parent. + principal: based on members of the program. + project_phase_any: based on the project phases active in a program. + project_status_code: based on status code of the program + storage_id: filters programs by linked storages + storage_url: filters programs by linked storages identified by the host url + type_id: based on the types active in a program. + user_action: based on the actions the current user has in the program. + visible: based on the visibility for the user (id) provided as the filter value. This filter is useful for admins to identify the programs visible to a user.  There might also be additional filters based on the custom fields that have been configured.  Each defined lifecycle step will also define a filter in this list endpoint. Given that the elements are not static but rather dynamically created on each OpenProject instance, a list cannot be provided. Those filters follow the schema: + project_start_gate_[id]: a filter on a project phase's start gate active in a program. The id is the id of the phase the gate belongs to. + project_finish_gate_[id]: a filter on a project phase's finish gate active in a program. The id is the id of the phase the gate belongs to. + project_phase_[id]: a filter on a project phase active in a program. The id is the id of the phase queried for. (optional)
    sort_by = '[[\"id\", \"asc\"]]' # str | JSON specifying sort criteria. Currently supported orders are:  + id + name + typeahead (sorting by hierarchy and name) + created_at + public + latest_activity_at + required_disk_space  There might also be additional orders based on the custom fields that have been configured. (optional)
    select = 'total,elements/identifier,elements/name' # str | Comma separated list of properties to include. (optional)

    try:
        # List programs
        api_response = api_instance.list_programs(filters=filters, sort_by=sort_by, select=select)
        print("The response of ProgramsApi->list_programs:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProgramsApi->list_programs: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **filters** | **str**| JSON specifying filter conditions. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported filters are:  + active: based on the active property of the program + ancestor: filters programs by their ancestor. A program is not considered to be its own ancestor. + available_project_attributes: filters programs based on the activated project attributes. + created_at: based on the time the program was created + favorited: based on the favorited property of the program + id: based on programs&#39; id. + latest_activity_at: based on the time the last activity was registered on a program. + name_and_identifier: based on both the name and the identifier. + parent_id: filters programs by their parent. + principal: based on members of the program. + project_phase_any: based on the project phases active in a program. + project_status_code: based on status code of the program + storage_id: filters programs by linked storages + storage_url: filters programs by linked storages identified by the host url + type_id: based on the types active in a program. + user_action: based on the actions the current user has in the program. + visible: based on the visibility for the user (id) provided as the filter value. This filter is useful for admins to identify the programs visible to a user.  There might also be additional filters based on the custom fields that have been configured.  Each defined lifecycle step will also define a filter in this list endpoint. Given that the elements are not static but rather dynamically created on each OpenProject instance, a list cannot be provided. Those filters follow the schema: + project_start_gate_[id]: a filter on a project phase&#39;s start gate active in a program. The id is the id of the phase the gate belongs to. + project_finish_gate_[id]: a filter on a project phase&#39;s finish gate active in a program. The id is the id of the phase the gate belongs to. + project_phase_[id]: a filter on a project phase active in a program. The id is the id of the phase queried for. | [optional] 
 **sort_by** | **str**| JSON specifying sort criteria. Currently supported orders are:  + id + name + typeahead (sorting by hierarchy and name) + created_at + public + latest_activity_at + required_disk_space  There might also be additional orders based on the custom fields that have been configured. | [optional] 
 **select** | **str**| Comma separated list of properties to include. | [optional] 

### Return type

[**ProgramCollectionModel**](ProgramCollectionModel.md)

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

# **program_update_form**
> program_update_form(id, body=body)

Program update form



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
    api_instance = openproject_client.ProgramsApi(api_client)
    id = 1 # int | Program id
    body = None # object |  (optional)

    try:
        # Program update form
        api_instance.program_update_form(id, body=body)
    except Exception as e:
        print("Exception when calling ProgramsApi->program_update_form: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Program id | 
 **body** | **object**|  | [optional] 

### Return type

void (empty response body)

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
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** edit workspace in the program |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_program**
> ProgramModel update_program(id, program_model=program_model)

Update Program

Updates the given program by applying the attributes provided in the body.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.program_model import ProgramModel
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
    api_instance = openproject_client.ProgramsApi(api_client)
    id = 1 # int | Program id
    program_model = openproject_client.ProgramModel() # ProgramModel |  (optional)

    try:
        # Update Program
        api_response = api_instance.update_program(id, program_model=program_model)
        print("The response of ProgramsApi->update_program:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProgramsApi->update_program: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Program id | 
 **program_model** | [**ProgramModel**](ProgramModel.md)|  | [optional] 

### Return type

[**ProgramModel**](ProgramModel.md)

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
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** edit project for the program to be altered |  -  |
**404** | Returned if the program does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view project  *Note: A client without sufficient permissions shall not be able to test for the existence of a version. That&#39;s why a 404 is returned here, even if a 403 might be more appropriate.* |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |
**422** | Returned if:  * a constraint for a property was violated (&#x60;PropertyConstraintViolation&#x60;) |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **view_program**
> ProgramModel view_program(id)

View program



### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.program_model import ProgramModel
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
    api_instance = openproject_client.ProgramsApi(api_client)
    id = 1 # int | Program id

    try:
        # View program
        api_response = api_instance.view_program(id)
        print("The response of ProgramsApi->view_program:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProgramsApi->view_program: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Program id | 

### Return type

[**ProgramModel**](ProgramModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**404** | Returned if the program does not exist or the client does not have sufficient permissions to see it.  **Required permission:** any permission in the program  *Note: A client without sufficient permissions shall not be able to test for the existence of a program. That&#39;s why a 404 is returned here, even if a 403 might be more appropriate.* |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

