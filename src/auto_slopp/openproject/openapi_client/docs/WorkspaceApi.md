# auto_slopp.openproject.openapi_client.WorkspaceApi

All URIs are relative to *https://openproject.melvin.beer*

Method | HTTP request | Description
------------- | ------------- | -------------
[**list_workspace**](WorkspaceApi.md#list_workspace) | **GET** /api/v3/workspaces | List workspace


# **list_workspace**
> WorkspaceCollectionModel list_workspace(filters=filters, sort_by=sort_by, select=select)

List workspace

Returns a collection of workspaces. The collection can be filtered via query parameters similar to how work packages are filtered. In addition to the provided filter, the result set is always limited to only contain workspaces the client is allowed to see.
Since workspaces are the generic term for a number of resources like projects and portfolios, the returned collection will contain a mix of those resources.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.workspace_collection_model import WorkspaceCollectionModel
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
    api_instance = auto_slopp.openproject.openapi_client.WorkspaceApi(api_client)
    filters = '[{ \"ancestor\": { \"operator\": \"=\", \"values\": [\"1\"] }\" }]' # str | JSON specifying filter conditions. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported filters are:  + active: based on the active property of the workspace + ancestor: filters workspace by their ancestor. A workspace is not considered to be its own ancestor. + available_project_attributes: filters workspace based on the activated project attributes. + created_at: based on the time the workspace was created + favorited: based on the favorited property of the workspace + id: based on workspace' id. + latest_activity_at: based on the time the last activity was registered on a workspace. + name_and_identifier: based on both the name and the identifier. + parent_id: filters workspace by their parent. + principal: based on members of the workspace. + project_phase_any: based on the project phases active in a workspace. + project_status_code: based on status code of the workspace + storage_id: filters workspace by linked storages + storage_url: filters workspace by linked storages identified by the host url + type_id: based on the types active in a workspace. + user_action: based on the actions the current user has in the workspace. + visible: based on the visibility for the user (id) provided as the filter value. This filter is useful for admins to identify the workspace visible to a user.  There might also be additional filters based on the custom fields that have been configured.  Each defined lifecycle step will also define a filter in this list endpoint. Given that the elements are not static but rather dynamically created on each OpenProject instance, a list cannot be provided. Those filters follow the schema: + project_start_gate_[id]: a filter on a project phase's start gate active in a workspace. The id is the id of the phase the gate belongs to. + project_finish_gate_[id]: a filter on a project phase's finish gate active in a workspace. The id is the id of the phase the gate belongs to. + project_phase_[id]: a filter on a project phase active in a workspace. The id is the id of the phase queried for. (optional)
    sort_by = '[[\"id\", \"asc\"]]' # str | JSON specifying sort criteria. Currently supported orders are:  + id + name + typeahead (sorting by hierarchy and name) + created_at + public + latest_activity_at + required_disk_space  There might also be additional orders based on the custom fields that have been configured. (optional)
    select = 'total,elements/identifier,elements/name' # str | Comma separated list of properties to include. (optional)

    try:
        # List workspace
        api_response = api_instance.list_workspace(filters=filters, sort_by=sort_by, select=select)
        print("The response of WorkspaceApi->list_workspace:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkspaceApi->list_workspace: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **filters** | **str**| JSON specifying filter conditions. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported filters are:  + active: based on the active property of the workspace + ancestor: filters workspace by their ancestor. A workspace is not considered to be its own ancestor. + available_project_attributes: filters workspace based on the activated project attributes. + created_at: based on the time the workspace was created + favorited: based on the favorited property of the workspace + id: based on workspace&#39; id. + latest_activity_at: based on the time the last activity was registered on a workspace. + name_and_identifier: based on both the name and the identifier. + parent_id: filters workspace by their parent. + principal: based on members of the workspace. + project_phase_any: based on the project phases active in a workspace. + project_status_code: based on status code of the workspace + storage_id: filters workspace by linked storages + storage_url: filters workspace by linked storages identified by the host url + type_id: based on the types active in a workspace. + user_action: based on the actions the current user has in the workspace. + visible: based on the visibility for the user (id) provided as the filter value. This filter is useful for admins to identify the workspace visible to a user.  There might also be additional filters based on the custom fields that have been configured.  Each defined lifecycle step will also define a filter in this list endpoint. Given that the elements are not static but rather dynamically created on each OpenProject instance, a list cannot be provided. Those filters follow the schema: + project_start_gate_[id]: a filter on a project phase&#39;s start gate active in a workspace. The id is the id of the phase the gate belongs to. + project_finish_gate_[id]: a filter on a project phase&#39;s finish gate active in a workspace. The id is the id of the phase the gate belongs to. + project_phase_[id]: a filter on a project phase active in a workspace. The id is the id of the phase queried for. | [optional] 
 **sort_by** | **str**| JSON specifying sort criteria. Currently supported orders are:  + id + name + typeahead (sorting by hierarchy and name) + created_at + public + latest_activity_at + required_disk_space  There might also be additional orders based on the custom fields that have been configured. | [optional] 
 **select** | **str**| Comma separated list of properties to include. | [optional] 

### Return type

[**WorkspaceCollectionModel**](WorkspaceCollectionModel.md)

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

