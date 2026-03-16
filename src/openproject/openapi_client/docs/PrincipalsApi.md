# openproject_client.PrincipalsApi

All URIs are relative to *https://openproject.melvin.beer*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_placeholder_user**](PrincipalsApi.md#create_placeholder_user) | **POST** /api/v3/placeholder_users | Create placeholder user
[**create_user**](PrincipalsApi.md#create_user) | **POST** /api/v3/users | Create User
[**delete_placeholder_user**](PrincipalsApi.md#delete_placeholder_user) | **DELETE** /api/v3/placeholder_users/{id} | Delete placeholder user
[**delete_user**](PrincipalsApi.md#delete_user) | **DELETE** /api/v3/users/{id} | Delete user
[**list_placeholder_users**](PrincipalsApi.md#list_placeholder_users) | **GET** /api/v3/placeholder_users | List placehoder users
[**list_principals**](PrincipalsApi.md#list_principals) | **GET** /api/v3/principals | List principals
[**list_users**](PrincipalsApi.md#list_users) | **GET** /api/v3/users | List Users
[**update_placeholder_user**](PrincipalsApi.md#update_placeholder_user) | **PATCH** /api/v3/placeholder_users/{id} | Update placeholder user
[**update_user**](PrincipalsApi.md#update_user) | **PATCH** /api/v3/users/{id} | Update user
[**view_placeholder_user**](PrincipalsApi.md#view_placeholder_user) | **GET** /api/v3/placeholder_users/{id} | View placeholder user
[**view_user**](PrincipalsApi.md#view_user) | **GET** /api/v3/users/{id} | View user


# **create_placeholder_user**
> PlaceholderUserModel create_placeholder_user(placeholder_user_create_model=placeholder_user_create_model)

Create placeholder user

Creates a new placeholder user. Only administrators and users with `manage_placeholder_user` global permission are
allowed to do so. When calling this endpoint the client provides a single object, containing at least the
properties and links that are required, in the body.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.placeholder_user_create_model import PlaceholderUserCreateModel
from openproject_client.models.placeholder_user_model import PlaceholderUserModel
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
    api_instance = openproject_client.PrincipalsApi(api_client)
    placeholder_user_create_model = openproject_client.PlaceholderUserCreateModel() # PlaceholderUserCreateModel |  (optional)

    try:
        # Create placeholder user
        api_response = api_instance.create_placeholder_user(placeholder_user_create_model=placeholder_user_create_model)
        print("The response of PrincipalsApi->create_placeholder_user:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrincipalsApi->create_placeholder_user: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **placeholder_user_create_model** | [**PlaceholderUserCreateModel**](PlaceholderUserCreateModel.md)|  | [optional] 

### Return type

[**PlaceholderUserModel**](PlaceholderUserModel.md)

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

# **create_user**
> UserModel create_user(user_create_model=user_create_model)

Create User

Creates a new user. Only administrators and users with manage_user global permission are allowed to do so.
When calling this endpoint the client provides a single object, containing at least the properties and links that are required, in the body.

Valid values for `status`:

1) "active" - In this case a password has to be provided in addition to the other attributes.

2) "invited" - In this case nothing but the email address is required. The rest is optional. An invitation will be sent to the user.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.user_create_model import UserCreateModel
from openproject_client.models.user_model import UserModel
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
    api_instance = openproject_client.PrincipalsApi(api_client)
    user_create_model = openproject_client.UserCreateModel() # UserCreateModel |  (optional)

    try:
        # Create User
        api_response = api_instance.create_user(user_create_model=user_create_model)
        print("The response of PrincipalsApi->create_user:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrincipalsApi->create_user: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_create_model** | [**UserCreateModel**](UserCreateModel.md)|  | [optional] 

### Return type

[**UserModel**](UserModel.md)

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

# **delete_placeholder_user**
> delete_placeholder_user(id)

Delete placeholder user

Set the specified placeholder user to deleted status.

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
    api_instance = openproject_client.PrincipalsApi(api_client)
    id = 1 # int | Placeholder user id

    try:
        # Delete placeholder user
        api_instance.delete_placeholder_user(id)
    except Exception as e:
        print("Exception when calling PrincipalsApi->delete_placeholder_user: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Placeholder user id | 

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
**202** | Returned if the group was marked for deletion.  Note that the response body is empty as of now. In future versions of the API a body *might* be returned, indicating the progress of deletion. |  -  |
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** &#x60;manage_placeholder_users&#x60; |  -  |
**404** | Returned if the placeholder user does not exist. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_user**
> delete_user(id)

Delete user

Permanently deletes the specified user account.

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
    api_instance = openproject_client.PrincipalsApi(api_client)
    id = 1 # int | User id

    try:
        # Delete user
        api_instance.delete_user(id)
    except Exception as e:
        print("Exception when calling PrincipalsApi->delete_user: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| User id | 

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
**202** | Returned if the account was deleted successfully.  Note that the response body is empty as of now. In future versions of the API a body *might* be returned, indicating the progress of deletion. |  -  |
**403** | Returned if the client does not have sufficient permissions or if deletion of users was disabled in the instance wide settings.  **Required permission:** Administrators only (exception: users might be able to delete their own accounts) |  -  |
**404** | Returned if the user does not exist. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_placeholder_users**
> PrincipalCollectionModel list_placeholder_users(filters=filters, select=select)

List placehoder users

List all placeholder users. This can only be accessed if the requesting user has the global permission
`manage_placeholder_user` or `manage_members` in any project.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.principal_collection_model import PrincipalCollectionModel
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
    api_instance = openproject_client.PrincipalsApi(api_client)
    filters = '[{ \"name\": { \"operator\": \"~\", \"values\": [\"Darth\"] } }]' # str | JSON specifying filter conditions. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported filters are:  - name: filters placeholder users by the name. - group: filters placeholder by the group it is contained in. - status: filters placeholder by the status it has. (optional)
    select = 'total,elements/name,elements/self,self' # str | Comma separated list of properties to include. (optional)

    try:
        # List placehoder users
        api_response = api_instance.list_placeholder_users(filters=filters, select=select)
        print("The response of PrincipalsApi->list_placeholder_users:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrincipalsApi->list_placeholder_users: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **filters** | **str**| JSON specifying filter conditions. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported filters are:  - name: filters placeholder users by the name. - group: filters placeholder by the group it is contained in. - status: filters placeholder by the status it has. | [optional] 
 **select** | **str**| Comma separated list of properties to include. | [optional] 

### Return type

[**PrincipalCollectionModel**](PrincipalCollectionModel.md)

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

# **list_principals**
> PrincipalCollectionModel list_principals(filters=filters, select=select)

List principals

List all principals. The client can choose to filter the principals similar to how work packages are filtered. In
addition to the provided filters, the server will reduce the result set to only contain principals who are members
in projects the client is allowed to see.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.principal_collection_model import PrincipalCollectionModel
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
    api_instance = openproject_client.PrincipalsApi(api_client)
    filters = '[{ \"type\": { \"operator\": \"=\", \"values\": [\"User\"] } }]' # str | JSON specifying filter conditions. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported filters are:  - type: filters principals by their type (*User*, *Group*, *PlaceholderUser*). - member: filters principals by the projects they are members in. - name: filters principals by the user or group name. - any_name_attribute: filters principals by the user or group first- and last name, email or login. - status: filters principals by their status number (active = *1*, registered = *2*, locked = *3*, invited = *4*) (optional)
    select = 'total,elements/name,elements/self,self' # str | Comma separated list of properties to include. (optional)

    try:
        # List principals
        api_response = api_instance.list_principals(filters=filters, select=select)
        print("The response of PrincipalsApi->list_principals:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrincipalsApi->list_principals: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **filters** | **str**| JSON specifying filter conditions. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported filters are:  - type: filters principals by their type (*User*, *Group*, *PlaceholderUser*). - member: filters principals by the projects they are members in. - name: filters principals by the user or group name. - any_name_attribute: filters principals by the user or group first- and last name, email or login. - status: filters principals by their status number (active &#x3D; *1*, registered &#x3D; *2*, locked &#x3D; *3*, invited &#x3D; *4*) | [optional] 
 **select** | **str**| Comma separated list of properties to include. | [optional] 

### Return type

[**PrincipalCollectionModel**](PrincipalCollectionModel.md)

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

# **list_users**
> UserCollectionModel list_users(offset=offset, page_size=page_size, filters=filters, sort_by=sort_by, select=select)

List Users

Lists users. Only administrators or users with the following global permission can access this resource:
- `manage_user`

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.user_collection_model import UserCollectionModel
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
    api_instance = openproject_client.PrincipalsApi(api_client)
    offset = 1 # int | Page number inside the requested collection. (optional) (default to 1)
    page_size = 25 # int | Number of elements to display per page. (optional)
    filters = '[{ \"status\": { \"operator\": \"=\", \"values\": [\"invited\"] } }, { \"group\": { \"operator\": \"=\", \"values\": [\"1\"] } }, { \"name\": { \"operator\": \"=\", \"values\": [\"h.wurst@openproject.com\"] } }]' # str | JSON specifying filter conditions. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported filters are:  + status: Status the user has  + group: Name of the group in which to-be-listed users are members.  + name: Filter users in whose first or last names, or email addresses the given string occurs.  + login: User's login (optional)
    sort_by = '[[\"status\", \"asc\"]]' # str | JSON specifying sort criteria. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. (optional)
    select = 'total,elements/name,elements/self,self' # str | Comma separated list of properties to include. (optional)

    try:
        # List Users
        api_response = api_instance.list_users(offset=offset, page_size=page_size, filters=filters, sort_by=sort_by, select=select)
        print("The response of PrincipalsApi->list_users:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrincipalsApi->list_users: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **offset** | **int**| Page number inside the requested collection. | [optional] [default to 1]
 **page_size** | **int**| Number of elements to display per page. | [optional] 
 **filters** | **str**| JSON specifying filter conditions. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported filters are:  + status: Status the user has  + group: Name of the group in which to-be-listed users are members.  + name: Filter users in whose first or last names, or email addresses the given string occurs.  + login: User&#39;s login | [optional] 
 **sort_by** | **str**| JSON specifying sort criteria. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. | [optional] 
 **select** | **str**| Comma separated list of properties to include. | [optional] 

### Return type

[**UserCollectionModel**](UserCollectionModel.md)

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
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** Administrator or any of: &#39;manage_members&#39;, &#39;manage_user&#39;, &#39;share_work_packages&#39;. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_placeholder_user**
> PlaceholderUserModel update_placeholder_user(id, placeholder_user_create_model=placeholder_user_create_model)

Update placeholder user

Updates the placeholder user's writable attributes.
When calling this endpoint the client provides a single object, containing at least the properties and links
that are required, in the body.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.placeholder_user_create_model import PlaceholderUserCreateModel
from openproject_client.models.placeholder_user_model import PlaceholderUserModel
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
    api_instance = openproject_client.PrincipalsApi(api_client)
    id = 1 # int | Placeholder user id
    placeholder_user_create_model = openproject_client.PlaceholderUserCreateModel() # PlaceholderUserCreateModel |  (optional)

    try:
        # Update placeholder user
        api_response = api_instance.update_placeholder_user(id, placeholder_user_create_model=placeholder_user_create_model)
        print("The response of PrincipalsApi->update_placeholder_user:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrincipalsApi->update_placeholder_user: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Placeholder user id | 
 **placeholder_user_create_model** | [**PlaceholderUserCreateModel**](PlaceholderUserCreateModel.md)|  | [optional] 

### Return type

[**PlaceholderUserModel**](PlaceholderUserModel.md)

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
**403** | Returned if the client does not have sufficient permissions.  **Required permission**: &#x60;manage_placeholder_users&#x60; |  -  |
**404** | Returned if the placeholder user does not exist. |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |
**422** | Returned if:  - the client tries to modify a read-only property (&#x60;PropertyIsReadOnly&#x60;) - a constraint for a property was violated (&#x60;PropertyConstraintViolation&#x60;) |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_user**
> UserModel update_user(id, user_create_model=user_create_model)

Update user

Updates the user's writable attributes.
When calling this endpoint the client provides a single object, containing at least the properties and links that are required, in the body.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.user_create_model import UserCreateModel
from openproject_client.models.user_model import UserModel
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
    api_instance = openproject_client.PrincipalsApi(api_client)
    id = 1 # int | User id
    user_create_model = openproject_client.UserCreateModel() # UserCreateModel |  (optional)

    try:
        # Update user
        api_response = api_instance.update_user(id, user_create_model=user_create_model)
        print("The response of PrincipalsApi->update_user:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrincipalsApi->update_user: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| User id | 
 **user_create_model** | [**UserCreateModel**](UserCreateModel.md)|  | [optional] 

### Return type

[**UserModel**](UserModel.md)

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
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** Administrators, manage_user global permission |  -  |
**404** | Returned if the user does not exist or if the API user does not have the necessary permissions to update it.  **Required permission:** Administrators only (exception: users may update their own accounts) |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |
**422** | Returned if:  * the client tries to modify a read-only property (&#x60;PropertyIsReadOnly&#x60;)  * a constraint for a property was violated (&#x60;PropertyConstraintViolation&#x60;) |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **view_placeholder_user**
> PlaceholderUserModel view_placeholder_user(id)

View placeholder user

Return the placeholder user resource.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.placeholder_user_model import PlaceholderUserModel
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
    api_instance = openproject_client.PrincipalsApi(api_client)
    id = '1' # str | The placeholder user id

    try:
        # View placeholder user
        api_response = api_instance.view_placeholder_user(id)
        print("The response of PrincipalsApi->view_placeholder_user:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrincipalsApi->view_placeholder_user: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| The placeholder user id | 

### Return type

[**PlaceholderUserModel**](PlaceholderUserModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**404** | Returned if the user does not exist or if the API user does not have permission to view them.  **Required permission**: &#x60;manage_placeholder_users&#x60; |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **view_user**
> UserModel view_user(id)

View user



### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.user_model import UserModel
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
    api_instance = openproject_client.PrincipalsApi(api_client)
    id = '1' # str | User id. Use `me` to reference current user, if any.

    try:
        # View user
        api_response = api_instance.view_user(id)
        print("The response of PrincipalsApi->view_user:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrincipalsApi->view_user: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| User id. Use &#x60;me&#x60; to reference current user, if any. | 

### Return type

[**UserModel**](UserModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**404** | Returned if the user does not exist or if the API user does not have permission to view them.  **Required permission** The user needs to be locked in if the installation is configured to prevent anonymous access |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

