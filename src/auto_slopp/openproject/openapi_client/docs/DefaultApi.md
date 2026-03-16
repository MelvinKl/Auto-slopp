# auto_slopp.openproject.openapi_client.DefaultApi

All URIs are relative to *https://openproject.melvin.beer*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_custom_field_item**](DefaultApi.md#get_custom_field_item) | **GET** /api/v3/custom_field_items/{id} | Get a custom field hierarchy item
[**get_custom_field_item_branch**](DefaultApi.md#get_custom_field_item_branch) | **GET** /api/v3/custom_field_items/{id}/branch | Get a custom field hierarchy item&#39;s branch
[**get_custom_field_items**](DefaultApi.md#get_custom_field_items) | **GET** /api/v3/custom_fields/{id}/items | Get the custom field hierarchy items


# **get_custom_field_item**
> HierarchyItemReadModel get_custom_field_item(id)

Get a custom field hierarchy item

Retrieves a single custom field item specified by its unique identifier.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.hierarchy_item_read_model import HierarchyItemReadModel
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
    api_instance = auto_slopp.openproject.openapi_client.DefaultApi(api_client)
    id = 42 # int | The custom field item's unique identifier

    try:
        # Get a custom field hierarchy item
        api_response = api_instance.get_custom_field_item(id)
        print("The response of DefaultApi->get_custom_field_item:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_custom_field_item: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| The custom field item&#39;s unique identifier | 

### Return type

[**HierarchyItemReadModel**](HierarchyItemReadModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**403** | Returned if the user is not logged in. |  -  |
**404** | Returned if the custom field item does not exist or the user lacks permission to see it.  The permission required to view the item depends on the custom field it belongs to. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_custom_field_item_branch**
> HierarchyItemCollectionModel get_custom_field_item_branch(id)

Get a custom field hierarchy item's branch

Retrieves the branch of a single custom field item specified by its unique identifier.

A branch is list of all ancestors, starting with the root item and finishing with the item itself.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.hierarchy_item_collection_model import HierarchyItemCollectionModel
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
    api_instance = auto_slopp.openproject.openapi_client.DefaultApi(api_client)
    id = 42 # int | The custom field item's unique identifier

    try:
        # Get a custom field hierarchy item's branch
        api_response = api_instance.get_custom_field_item_branch(id)
        print("The response of DefaultApi->get_custom_field_item_branch:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_custom_field_item_branch: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| The custom field item&#39;s unique identifier | 

### Return type

[**HierarchyItemCollectionModel**](HierarchyItemCollectionModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**403** | Returned if the user is not logged in. |  -  |
**404** | Returned if the custom field does not exist or the user lacks permission to view it. |  -  |
**422** | Returned if the custom field is not of type hierarchy. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_custom_field_items**
> HierarchyItemCollectionModel get_custom_field_items(id, parent=parent, depth=depth)

Get the custom field hierarchy items

Retrieves the hierarchy of custom fields.

The hierarchy is a tree structure of hierarchy items. It is represented as a flat list of items, where each item
has a reference to its parent and children. The list is ordered in a depth-first manner. The first item is the
requested parent. If parent was unset, the root item is returned as first element.

Passing the `depth` query parameter allows to limit the depth of the hierarchy. If the depth is unset, the full
hierarchy tree is returned. If the depth is set to `0`, only the requested parent is returned. Any other positive
integer will return the number of children levels specified by this value.

This endpoint only returns, if the custom field is of type `hierarchy`.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.hierarchy_item_collection_model import HierarchyItemCollectionModel
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
    api_instance = auto_slopp.openproject.openapi_client.DefaultApi(api_client)
    id = 42 # int | The custom field's unique identifier
    parent = 1337 # int | The identifier of the parent hierarchy item (optional)
    depth = 1 # int | The level of hierarchy depth (optional)

    try:
        # Get the custom field hierarchy items
        api_response = api_instance.get_custom_field_items(id, parent=parent, depth=depth)
        print("The response of DefaultApi->get_custom_field_items:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_custom_field_items: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| The custom field&#39;s unique identifier | 
 **parent** | **int**| The identifier of the parent hierarchy item | [optional] 
 **depth** | **int**| The level of hierarchy depth | [optional] 

### Return type

[**HierarchyItemCollectionModel**](HierarchyItemCollectionModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**403** | Returned if the user is not logged in. |  -  |
**404** | Returned if the custom field does not exist or the user lacks the permission to view it. |  -  |
**422** | Returned if the custom field is not of type hierarchy. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

