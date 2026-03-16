# openproject_client.RelationsApi

All URIs are relative to *https://openproject.melvin.beer*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_relation**](RelationsApi.md#create_relation) | **POST** /api/v3/work_packages/{id}/relations | Create relation
[**delete_relation**](RelationsApi.md#delete_relation) | **DELETE** /api/v3/relations/{id} | Delete Relation
[**get_relation**](RelationsApi.md#get_relation) | **GET** /api/v3/relations/{id} | Get Relation
[**list_relations**](RelationsApi.md#list_relations) | **GET** /api/v3/relations | List Relations
[**update_relation**](RelationsApi.md#update_relation) | **PATCH** /api/v3/relations/{id} | Update Relation


# **create_relation**
> RelationReadModel create_relation(id, relation_write_model=relation_write_model)

Create relation

Create a work package relation on the given work package. A successful creation will result in a relation between
two work packages, thus appearing on both involved work package resources.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.relation_read_model import RelationReadModel
from openproject_client.models.relation_write_model import RelationWriteModel
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
    api_instance = openproject_client.RelationsApi(api_client)
    id = 1 # int | Work package id
    relation_write_model = openproject_client.RelationWriteModel() # RelationWriteModel |  (optional)

    try:
        # Create relation
        api_response = api_instance.create_relation(id, relation_write_model=relation_write_model)
        print("The response of RelationsApi->create_relation:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RelationsApi->create_relation: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Work package id | 
 **relation_write_model** | [**RelationWriteModel**](RelationWriteModel.md)|  | [optional] 

### Return type

[**RelationReadModel**](RelationReadModel.md)

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
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** manage work package relations |  -  |
**409** | Returned if there already exists a relation between the given work packages of **any** type or if the relation is not allowed. |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |
**422** | Returned if:  - the client tries to write a read-only property (&#x60;PropertyIsReadOnly&#x60;) - a constraint for a property was violated (&#x60;PropertyConstraintViolation&#x60;) - the client provides a link to an invalid resource (&#x60;ResourceTypeMismatch&#x60;) |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_relation**
> delete_relation(id)

Delete Relation

Deletes the relation.

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
    api_instance = openproject_client.RelationsApi(api_client)
    id = 1 # int | The unique identifier of the relation resource

    try:
        # Delete Relation
        api_instance.delete_relation(id)
    except Exception as e:
        print("Exception when calling RelationsApi->delete_relation: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| The unique identifier of the relation resource | 

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
**204** | Returned if the relation was deleted successfully. The response body is empty. |  -  |
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** manage work package relations |  -  |
**404** | Returned if the relation does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view work packages |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_relation**
> RelationReadModel get_relation(id)

Get Relation

Get a single relation specified by its unique identifier.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.relation_read_model import RelationReadModel
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
    api_instance = openproject_client.RelationsApi(api_client)
    id = 1 # int | Relation id

    try:
        # Get Relation
        api_response = api_instance.get_relation(id)
        print("The response of RelationsApi->get_relation:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RelationsApi->get_relation: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Relation id | 

### Return type

[**RelationReadModel**](RelationReadModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**404** | Returned if the relation does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view work packages for the involved work packages |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_relations**
> RelationCollectionModel list_relations(filters=filters, sort_by=sort_by)

List Relations

Lists all relations according to the given (optional, logically conjunctive) filters and ordered by ID.
The response only includes relations between work packages which the user is allowed to see.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.relation_collection_model import RelationCollectionModel
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
    api_instance = openproject_client.RelationsApi(api_client)
    filters = '[{ \"from\": { \"operator\": \"=\", \"values\": 42 }\" }]' # str | JSON specifying filter conditions. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Valid fields to filter by are:  - id - ID of relation - from - ID of work package from which the filtered relations emanates. - to - ID of work package to which this related points. - involved - ID of either the `from` or the `to` work package. - type - The type of relation to filter by, e.g. \"follows\". (optional)
    sort_by = '[[\"type\", \"asc\"]]' # str | JSON specifying sort criteria. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. (optional)

    try:
        # List Relations
        api_response = api_instance.list_relations(filters=filters, sort_by=sort_by)
        print("The response of RelationsApi->list_relations:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RelationsApi->list_relations: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **filters** | **str**| JSON specifying filter conditions. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Valid fields to filter by are:  - id - ID of relation - from - ID of work package from which the filtered relations emanates. - to - ID of work package to which this related points. - involved - ID of either the &#x60;from&#x60; or the &#x60;to&#x60; work package. - type - The type of relation to filter by, e.g. \&quot;follows\&quot;. | [optional] 
 **sort_by** | **str**| JSON specifying sort criteria. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. | [optional] 

### Return type

[**RelationCollectionModel**](RelationCollectionModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**400** | Returned if the client provides invalid filter parameters. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_relation**
> RelationReadModel update_relation(id, relation_write_model=relation_write_model)

Update Relation

When calling this endpoint the client provides a single object, containing the properties and links that it wants
to change, in the body. It is only allowed to provide properties or links supporting the **write** operation.

Note that changing the `type` of a relation invariably also changes the respective `reverseType` as well as the
"name" of it. The returned Relation object will reflect that change. For instance if you change a Relation's
`type` to "follows" then the `reverseType` will be changed to `precedes`.

It is not allowed to change a relation's involved work packages.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.relation_read_model import RelationReadModel
from openproject_client.models.relation_write_model import RelationWriteModel
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
    api_instance = openproject_client.RelationsApi(api_client)
    id = 1 # int | Relation ID
    relation_write_model = openproject_client.RelationWriteModel() # RelationWriteModel |  (optional)

    try:
        # Update Relation
        api_response = api_instance.update_relation(id, relation_write_model=relation_write_model)
        print("The response of RelationsApi->update_relation:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RelationsApi->update_relation: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Relation ID | 
 **relation_write_model** | [**RelationWriteModel**](RelationWriteModel.md)|  | [optional] 

### Return type

[**RelationReadModel**](RelationReadModel.md)

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
**404** | Returned if the relation does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view work packages |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |
**422** | Returned if:  - the client tries to modify a read-only property (&#x60;PropertyIsReadOnly&#x60;) - a constraint for a property was violated (&#x60;PropertyConstraintViolation&#x60;) - the client provides a link to an invalid resource (&#x60;ResourceTypeMismatch&#x60;) or a   work package that does not exist or for which the client does not have sufficient permissions   to see it (**required permissions**: &#x60;view work packages&#x60; for the involved work packages). |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

