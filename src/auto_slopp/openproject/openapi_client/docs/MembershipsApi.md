# auto_slopp.openproject.openapi_client.MembershipsApi

All URIs are relative to *https://openproject.melvin.beer*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_membership**](MembershipsApi.md#create_membership) | **POST** /api/v3/memberships | Create a membership
[**delete_membership**](MembershipsApi.md#delete_membership) | **DELETE** /api/v3/memberships/{id} | Delete membership
[**form_create_membership**](MembershipsApi.md#form_create_membership) | **POST** /api/v3/memberships/form | Form create membership
[**form_update_membership**](MembershipsApi.md#form_update_membership) | **POST** /api/v3/memberships/{id}/form | Form update membership
[**get_membership**](MembershipsApi.md#get_membership) | **GET** /api/v3/memberships/{id} | Get a membership
[**get_membership_schema**](MembershipsApi.md#get_membership_schema) | **GET** /api/v3/memberships/schema | Schema membership
[**get_memberships_available_projects**](MembershipsApi.md#get_memberships_available_projects) | **GET** /api/v3/memberships/available_projects | Available projects for memberships
[**list_memberships**](MembershipsApi.md#list_memberships) | **GET** /api/v3/memberships | List memberships
[**update_membership**](MembershipsApi.md#update_membership) | **PATCH** /api/v3/memberships/{id} | Update membership


# **create_membership**
> MembershipReadModel create_membership(membership_write_model=membership_write_model)

Create a membership

Creates a new membership applying the attributes provided in the body.

You can use the form and schema to retrieve the valid attribute values and by that be guided towards successful
creation.

By providing a `notificationMessage` within the `_meta` block of the payload, the client can include a customized
message to the user of the newly created membership. In case of a group, the message will be sent to every user
belonging to the group.

By including `{ "sendNotifications": false }` within the `_meta` block of the payload, no notifications is send
out at all.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.membership_read_model import MembershipReadModel
from auto_slopp.openproject.openapi_client.models.membership_write_model import MembershipWriteModel
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
    api_instance = auto_slopp.openproject.openapi_client.MembershipsApi(api_client)
    membership_write_model = auto_slopp.openproject.openapi_client.MembershipWriteModel() # MembershipWriteModel |  (optional)

    try:
        # Create a membership
        api_response = api_instance.create_membership(membership_write_model=membership_write_model)
        print("The response of MembershipsApi->create_membership:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MembershipsApi->create_membership: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **membership_write_model** | [**MembershipWriteModel**](MembershipWriteModel.md)|  | [optional] 

### Return type

[**MembershipReadModel**](MembershipReadModel.md)

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
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** Manage members |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |
**422** | Returned if:  - a constraint for a property was violated (&#x60;PropertyConstraintViolation&#x60;) |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_membership**
> delete_membership(id)

Delete membership

Deletes the membership.

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
    api_instance = auto_slopp.openproject.openapi_client.MembershipsApi(api_client)
    id = 1 # int | Membership id

    try:
        # Delete membership
        api_instance.delete_membership(id)
    except Exception as e:
        print("Exception when calling MembershipsApi->delete_membership: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Membership id | 

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
**204** | Returned if the membership was successfully deleted |  -  |
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** manage members |  -  |
**404** | Returned if the membership does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view members  *Note: A client without sufficient permissions shall not be able to test for the existence of a version. That&#39;s why a 404 is returned here, even if a 403 might be more appropriate.* |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **form_create_membership**
> MembershipFormModel form_create_membership(membership_write_model=membership_write_model)

Form create membership

Requests and validates the creation form for memberships. The request payload, if sent, is validated. The form
endpoint itself does not create a membership.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.membership_form_model import MembershipFormModel
from auto_slopp.openproject.openapi_client.models.membership_write_model import MembershipWriteModel
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
    api_instance = auto_slopp.openproject.openapi_client.MembershipsApi(api_client)
    membership_write_model = auto_slopp.openproject.openapi_client.MembershipWriteModel() # MembershipWriteModel |  (optional)

    try:
        # Form create membership
        api_response = api_instance.form_create_membership(membership_write_model=membership_write_model)
        print("The response of MembershipsApi->form_create_membership:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MembershipsApi->form_create_membership: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **membership_write_model** | [**MembershipWriteModel**](MembershipWriteModel.md)|  | [optional] 

### Return type

[**MembershipFormModel**](MembershipFormModel.md)

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
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** manage memberships in any project |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **form_update_membership**
> MembershipReadModel form_update_membership(id, membership_write_model=membership_write_model)

Form update membership

Requests and validates the update form for a membership identified by the given id. The request payload, if sent,
is validated. The form endpoint itself does not change the membership.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.membership_read_model import MembershipReadModel
from auto_slopp.openproject.openapi_client.models.membership_write_model import MembershipWriteModel
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
    api_instance = auto_slopp.openproject.openapi_client.MembershipsApi(api_client)
    id = 1 # int | Membership id
    membership_write_model = auto_slopp.openproject.openapi_client.MembershipWriteModel() # MembershipWriteModel |  (optional)

    try:
        # Form update membership
        api_response = api_instance.form_update_membership(id, membership_write_model=membership_write_model)
        print("The response of MembershipsApi->form_update_membership:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MembershipsApi->form_update_membership: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Membership id | 
 **membership_write_model** | [**MembershipWriteModel**](MembershipWriteModel.md)|  | [optional] 

### Return type

[**MembershipReadModel**](MembershipReadModel.md)

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
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** manage versions in the version&#39;s project |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_membership**
> MembershipReadModel get_membership(id)

Get a membership

Retrieves a membership resource identified by the given id.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.membership_read_model import MembershipReadModel
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
    api_instance = auto_slopp.openproject.openapi_client.MembershipsApi(api_client)
    id = 1 # int | Membership id

    try:
        # Get a membership
        api_response = api_instance.get_membership(id)
        print("The response of MembershipsApi->get_membership:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MembershipsApi->get_membership: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Membership id | 

### Return type

[**MembershipReadModel**](MembershipReadModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**404** | Returned if the membership does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view members **or** manage members  *Note: A client without sufficient permissions shall not be able to test for the existence of a membership. That&#39;s why a 404 is returned here, even if a 403 might be more appropriate.* |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_membership_schema**
> MembershipSchemaModel get_membership_schema()

Schema membership

Retrieves the schema for the membership resource object.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.membership_schema_model import MembershipSchemaModel
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
    api_instance = auto_slopp.openproject.openapi_client.MembershipsApi(api_client)

    try:
        # Schema membership
        api_response = api_instance.get_membership_schema()
        print("The response of MembershipsApi->get_membership_schema:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MembershipsApi->get_membership_schema: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**MembershipSchemaModel**](MembershipSchemaModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**403** | Returned if the client does not have sufficient permissions to see the schema.  **Required permission:** manage members or view memberships on any project |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_memberships_available_projects**
> ProjectCollectionModel get_memberships_available_projects()

Available projects for memberships

Gets a list of projects in which a membership can be created in. The list contains all projects in which the user
issuing the request has the manage members permissions.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.project_collection_model import ProjectCollectionModel
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
    api_instance = auto_slopp.openproject.openapi_client.MembershipsApi(api_client)

    try:
        # Available projects for memberships
        api_response = api_instance.get_memberships_available_projects()
        print("The response of MembershipsApi->get_memberships_available_projects:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MembershipsApi->get_memberships_available_projects: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**ProjectCollectionModel**](ProjectCollectionModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** manage members |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_memberships**
> MembershipCollectionModel list_memberships(filters=filters, sort_by=sort_by)

List memberships

Returns a collection of memberships. The client can choose to filter
the memberships similar to how work packages are filtered. In addition to the
provided filters, the server will reduce the result set to only contain memberships,
for which the requesting client has sufficient permissions (*view_members*, *manage_members*).

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.membership_collection_model import MembershipCollectionModel
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
    api_instance = auto_slopp.openproject.openapi_client.MembershipsApi(api_client)
    filters = '[{ \"name\": { \"operator\": \"=\", \"values\": [\"A User\"] }\" }]' # str | JSON specifying filter conditions. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported filters are:  + any_name_attribute: filters memberships based on the name of the principal. All possible name variants   (and also email and login) are searched. + blocked: reduces the result set to all memberships that are temporarily blocked or that are not blocked   temporarily. + group: filters memberships based on the name of a group. The group however is not the principal used for   filtering. Rather, the memberships of the group are used as the filter values. + name: filters memberships based on the name of the principal. Note that only the name is used which depends   on a setting in the OpenProject instance. + principal: filters memberships based on the id of the principal. + project: filters memberships based on the id of the project. + role: filters memberships based on the id of any role assigned to the membership. + status: filters memberships based on the status of the principal. + created_at: filters memberships based on the time the membership was created. + updated_at: filters memberships based on the time the membership was updated last. (optional)
    sort_by = '[["id", "asc"]]' # str | JSON specifying sort criteria. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported sorts are:  + id: Sort by primary key + name: Sort by the name of the principal. Note that this depends on the setting for how the name is to be   displayed at least for users. + email: Sort by the email address of the principal. Groups and principal users, which do not have an email,   are sorted last. + status: Sort by the status of the principal. Groups and principal users, which do not have a status, are   sorted together with the active users. + created_at: Sort by membership creation datetime + updated_at: Sort by the time the membership was updated last (optional) (default to '[["id", "asc"]]')

    try:
        # List memberships
        api_response = api_instance.list_memberships(filters=filters, sort_by=sort_by)
        print("The response of MembershipsApi->list_memberships:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MembershipsApi->list_memberships: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **filters** | **str**| JSON specifying filter conditions. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported filters are:  + any_name_attribute: filters memberships based on the name of the principal. All possible name variants   (and also email and login) are searched. + blocked: reduces the result set to all memberships that are temporarily blocked or that are not blocked   temporarily. + group: filters memberships based on the name of a group. The group however is not the principal used for   filtering. Rather, the memberships of the group are used as the filter values. + name: filters memberships based on the name of the principal. Note that only the name is used which depends   on a setting in the OpenProject instance. + principal: filters memberships based on the id of the principal. + project: filters memberships based on the id of the project. + role: filters memberships based on the id of any role assigned to the membership. + status: filters memberships based on the status of the principal. + created_at: filters memberships based on the time the membership was created. + updated_at: filters memberships based on the time the membership was updated last. | [optional] 
 **sort_by** | **str**| JSON specifying sort criteria. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported sorts are:  + id: Sort by primary key + name: Sort by the name of the principal. Note that this depends on the setting for how the name is to be   displayed at least for users. + email: Sort by the email address of the principal. Groups and principal users, which do not have an email,   are sorted last. + status: Sort by the status of the principal. Groups and principal users, which do not have a status, are   sorted together with the active users. + created_at: Sort by membership creation datetime + updated_at: Sort by the time the membership was updated last | [optional] [default to &#39;[[&quot;id&quot;, &quot;asc&quot;]]&#39;]

### Return type

[**MembershipCollectionModel**](MembershipCollectionModel.md)

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

# **update_membership**
> MembershipReadModel update_membership(id, membership_write_model=membership_write_model)

Update membership

Updates the given membership by applying the attributes provided in the body.

By providing a `notificationMessage` within the `_meta` block of the payload, the client can include a customized message to the user
of the updated membership. In case of a group, the message will be sent to every user belonging to the group.

By including `{ "sendNotifications": false }` within the `_meta` block of the payload, no notifications is send out at all.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.membership_read_model import MembershipReadModel
from auto_slopp.openproject.openapi_client.models.membership_write_model import MembershipWriteModel
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
    api_instance = auto_slopp.openproject.openapi_client.MembershipsApi(api_client)
    id = 1 # int | Membership id
    membership_write_model = auto_slopp.openproject.openapi_client.MembershipWriteModel() # MembershipWriteModel |  (optional)

    try:
        # Update membership
        api_response = api_instance.update_membership(id, membership_write_model=membership_write_model)
        print("The response of MembershipsApi->update_membership:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MembershipsApi->update_membership: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Membership id | 
 **membership_write_model** | [**MembershipWriteModel**](MembershipWriteModel.md)|  | [optional] 

### Return type

[**MembershipReadModel**](MembershipReadModel.md)

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
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** Manage members in the membership&#39;s project. |  -  |
**404** | Returned if the membership does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view member  *Note: A client without sufficient permissions shall not be able to test for the existence of a version. That&#39;s why a 404 is returned here, even if a 403 might be more appropriate.* |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |
**422** | Returned if:  * a constraint for a property was violated (&#x60;PropertyConstraintViolation&#x60;) |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

