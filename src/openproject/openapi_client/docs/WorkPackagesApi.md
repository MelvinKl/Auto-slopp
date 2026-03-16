# openproject_client.WorkPackagesApi

All URIs are relative to *https://openproject.melvin.beer*

Method | HTTP request | Description
------------- | ------------- | -------------
[**add_watcher**](WorkPackagesApi.md#add_watcher) | **POST** /api/v3/work_packages/{id}/watchers | Add watcher
[**available_projects_for_work_package**](WorkPackagesApi.md#available_projects_for_work_package) | **GET** /api/v3/work_packages/{id}/available_projects | Available projects for work package
[**available_watchers**](WorkPackagesApi.md#available_watchers) | **GET** /api/v3/work_packages/{id}/available_watchers | Available watchers
[**comment_work_package**](WorkPackagesApi.md#comment_work_package) | **POST** /api/v3/work_packages/{id}/activities | Comment work package
[**create_project_work_package**](WorkPackagesApi.md#create_project_work_package) | **POST** /api/v3/projects/{id}/work_packages | Create work package in project
[**create_work_package**](WorkPackagesApi.md#create_work_package) | **POST** /api/v3/work_packages | Create Work Package
[**create_work_package_file_link**](WorkPackagesApi.md#create_work_package_file_link) | **POST** /api/v3/work_packages/{id}/file_links | Creates file links.
[**create_work_package_reminder**](WorkPackagesApi.md#create_work_package_reminder) | **POST** /api/v3/work_packages/{work_package_id}/reminders | Create a work package reminder
[**create_workspace_work_package**](WorkPackagesApi.md#create_workspace_work_package) | **POST** /api/v3/workspaces/{id}/work_packages | Create work package in workspace
[**delete_work_package**](WorkPackagesApi.md#delete_work_package) | **DELETE** /api/v3/work_packages/{id} | Delete Work Package
[**form_create_work_package**](WorkPackagesApi.md#form_create_work_package) | **POST** /api/v3/work_packages/form | Form for creating a Work Package
[**form_create_work_package_in_project**](WorkPackagesApi.md#form_create_work_package_in_project) | **POST** /api/v3/projects/{id}/work_packages/form | Form for creating Work Packages in a Project
[**form_create_work_package_in_workspace**](WorkPackagesApi.md#form_create_work_package_in_workspace) | **POST** /api/v3/workspaces/{id}/work_packages/form | Form for creating Work Packages in a Workspace
[**form_edit_work_package**](WorkPackagesApi.md#form_edit_work_package) | **POST** /api/v3/work_packages/{id}/form | Form for editing a Work Package
[**get_project_work_package_collection**](WorkPackagesApi.md#get_project_work_package_collection) | **GET** /api/v3/projects/{id}/work_packages | Get work packages of project
[**get_workspace_work_package_collection**](WorkPackagesApi.md#get_workspace_work_package_collection) | **GET** /api/v3/workspaces/{id}/work_packages | Get work packages of workspace
[**list_available_relation_candidates**](WorkPackagesApi.md#list_available_relation_candidates) | **GET** /api/v3/work_packages/{id}/available_relation_candidates | Available relation candidates
[**list_watchers**](WorkPackagesApi.md#list_watchers) | **GET** /api/v3/work_packages/{id}/watchers | List watchers
[**list_work_package_activities**](WorkPackagesApi.md#list_work_package_activities) | **GET** /api/v3/work_packages/{id}/activities | List work package activities
[**list_work_package_file_links**](WorkPackagesApi.md#list_work_package_file_links) | **GET** /api/v3/work_packages/{id}/file_links | Gets all file links of a work package
[**list_work_package_reminders**](WorkPackagesApi.md#list_work_package_reminders) | **GET** /api/v3/work_packages/{work_package_id}/reminders | List work package reminders
[**list_work_package_schemas**](WorkPackagesApi.md#list_work_package_schemas) | **GET** /api/v3/work_packages/schemas | List Work Package Schemas
[**list_work_packages**](WorkPackagesApi.md#list_work_packages) | **GET** /api/v3/work_packages | List work packages
[**project_available_assignees**](WorkPackagesApi.md#project_available_assignees) | **GET** /api/v3/projects/{id}/available_assignees | Project Available assignees
[**remove_watcher**](WorkPackagesApi.md#remove_watcher) | **DELETE** /api/v3/work_packages/{id}/watchers/{user_id} | Remove watcher
[**revisions**](WorkPackagesApi.md#revisions) | **GET** /api/v3/work_packages/{id}/revisions | Revisions
[**update_work_package**](WorkPackagesApi.md#update_work_package) | **PATCH** /api/v3/work_packages/{id} | Update a Work Package
[**view_work_package**](WorkPackagesApi.md#view_work_package) | **GET** /api/v3/work_packages/{id} | View Work Package
[**view_work_package_schema**](WorkPackagesApi.md#view_work_package_schema) | **GET** /api/v3/work_packages/schemas/{identifier} | View Work Package Schema
[**work_package_available_assignees**](WorkPackagesApi.md#work_package_available_assignees) | **GET** /api/v3/work_packages/{id}/available_assignees | Work Package Available assignees
[**workspace_available_assignees**](WorkPackagesApi.md#workspace_available_assignees) | **GET** /api/v3/workspaces/{id}/available_assignees | Workspace Available assignees


# **add_watcher**
> add_watcher(id, add_watcher_request=add_watcher_request)

Add watcher

Adds a watcher to the specified work package.

The request is expected to contain a single JSON object, that contains a link object under the `user` key.

The response will be user added as watcher.
In case the user was already watching the work package an `HTTP 200` is returned, an
`HTTP 201` if the user was added as a new watcher.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.add_watcher_request import AddWatcherRequest
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
    api_instance = openproject_client.WorkPackagesApi(api_client)
    id = 1 # int | Work package id
    add_watcher_request = openproject_client.AddWatcherRequest() # AddWatcherRequest |  (optional)

    try:
        # Add watcher
        api_instance.add_watcher(id, add_watcher_request=add_watcher_request)
    except Exception as e:
        print("Exception when calling WorkPackagesApi->add_watcher: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Work package id | 
 **add_watcher_request** | [**AddWatcherRequest**](AddWatcherRequest.md)|  | [optional] 

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
**201** | Created |  -  |
**400** | Occurs when the client did not send a valid JSON object in the request body.  For example:  * The request did not contain a single JSON object  * The JSON object did not contain the key &#x60;user&#x60;  * The value of &#x60;users&#x60; was not a link object |  -  |
**403** | Returned if the client does not have sufficient permissions.  **Required permissions:**  * view work package (for self)  * add work package watchers (for other users)  *Note that you will only receive this error, if you are at least allowed to see the corresponding work package.* |  -  |
**404** | Returned if the work package does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view work package  *Note that you will effectively not be able to change the watchers of a work package without being able to see the work package.* |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |
**422** | Returned if:  * the client tries to specify a link to a resource that is not a user (&#x60;ResourceTypeMismatch&#x60;)  * the user specified is not allowed to watch that work package (&#x60;PropertyConstraintViolation&#x60;)  * the user specified does not exist (&#x60;PropertyConstraintViolation&#x60;) |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **available_projects_for_work_package**
> object available_projects_for_work_package(id)

Available projects for work package

Gets a list of projects that are available as projects to which the work package can be moved.

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
    api_instance = openproject_client.WorkPackagesApi(api_client)
    id = 1 # int | work package id

    try:
        # Available projects for work package
        api_response = api_instance.available_projects_for_work_package(id)
        print("The response of WorkPackagesApi->available_projects_for_work_package:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkPackagesApi->available_projects_for_work_package: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| work package id | 

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
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** edit work package  *Note that you will only receive this error, if you are at least allowed to see the corresponding work package.* |  -  |
**404** | Returned if the work package does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view work package |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **available_watchers**
> object available_watchers(id)

Available watchers

Gets a list of users that are able to be watchers of the specified work package.

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
    api_instance = openproject_client.WorkPackagesApi(api_client)
    id = 1 # int | work package id

    try:
        # Available watchers
        api_response = api_instance.available_watchers(id)
        print("The response of WorkPackagesApi->available_watchers:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkPackagesApi->available_watchers: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| work package id | 

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
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** add work package watchers  *Note that you will only receive this error, if you are at least allowed to see the corresponding work package.* |  -  |
**404** | Returned if the work package does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view work package |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **comment_work_package**
> comment_work_package(id, notify=notify, activity_comment_write_model=activity_comment_write_model)

Comment work package

Creates an activity for the selected work package and, on success, returns the
updated activity.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.activity_comment_write_model import ActivityCommentWriteModel
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
    api_instance = openproject_client.WorkPackagesApi(api_client)
    id = 1 # int | Work package id
    notify = True # bool | Indicates whether change notifications (e.g. via E-Mail) should be sent. Note that this controls notifications for all users interested in changes to the work package (e.g. watchers, author and assignee), not just the current user. (optional) (default to True)
    activity_comment_write_model = openproject_client.ActivityCommentWriteModel() # ActivityCommentWriteModel |  (optional)

    try:
        # Comment work package
        api_instance.comment_work_package(id, notify=notify, activity_comment_write_model=activity_comment_write_model)
    except Exception as e:
        print("Exception when calling WorkPackagesApi->comment_work_package: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Work package id | 
 **notify** | **bool**| Indicates whether change notifications (e.g. via E-Mail) should be sent. Note that this controls notifications for all users interested in changes to the work package (e.g. watchers, author and assignee), not just the current user. | [optional] [default to True]
 **activity_comment_write_model** | [**ActivityCommentWriteModel**](ActivityCommentWriteModel.md)|  | [optional] 

### Return type

void (empty response body)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Created |  -  |
**400** | Occurs when the client did not send a valid JSON object in the request body. |  -  |
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** create journals  *Note that you will only receive this error, if you are at least allowed to see the corresponding work package.* |  -  |
**404** | Returned if the work package does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view work package |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_project_work_package**
> WorkPackageModel create_project_work_package(id, notify=notify, work_package_model=work_package_model)

Create work package in project

When calling this endpoint the client provides a single object, containing at least the properties and links that
are required, in the body. The required fields of a WorkPackage can be found in its schema, which is embedded in
the respective form. Note that it is only allowed to provide properties or links supporting the write operation.

This endpoint is deprecated and replaced by [`/api/v3/workspaces/{id}/work_packages`](https://www.openproject.org/docs/api/endpoints/work-packages/#create-work-package-in-workspace)

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.work_package_model import WorkPackageModel
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
    api_instance = openproject_client.WorkPackagesApi(api_client)
    id = 1 # int | Project id
    notify = True # bool | Indicates whether change notifications (e.g. via E-Mail) should be sent. Note that this controls notifications for all users interested in changes to the work package (e.g. watchers, author and assignee), not just the current user. (optional) (default to True)
    work_package_model = openproject_client.WorkPackageModel() # WorkPackageModel |  (optional)

    try:
        # Create work package in project
        api_response = api_instance.create_project_work_package(id, notify=notify, work_package_model=work_package_model)
        print("The response of WorkPackagesApi->create_project_work_package:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkPackagesApi->create_project_work_package: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Project id | 
 **notify** | **bool**| Indicates whether change notifications (e.g. via E-Mail) should be sent. Note that this controls notifications for all users interested in changes to the work package (e.g. watchers, author and assignee), not just the current user. | [optional] [default to True]
 **work_package_model** | [**WorkPackageModel**](WorkPackageModel.md)|  | [optional] 

### Return type

[**WorkPackageModel**](WorkPackageModel.md)

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
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** add work packages  *Note that you will only receive this error, if you are at least allowed to see the corresponding project.* |  -  |
**404** | Returned if the project does not exist or the client does not have sufficient permissions to see it.  **Required permissions:** view project  *Note: A client without sufficient permissions shall not be able to test for the existence of a project. That&#39;s why a 404 is returned here, even if a 403 might be more appropriate.* |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |
**422** | Returned if:  * the client tries to write a read-only property  * a constraint for a property was violated  * a property was provided in an unreadable format |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_work_package**
> WorkPackageModel create_work_package(notify=notify, work_package_model=work_package_model)

Create Work Package

When calling this endpoint the client provides a single object, containing at least the properties and links that are required, in the body.
The required fields of a WorkPackage can be found in its schema, which is embedded in the respective form.
Note that it is only allowed to provide properties or links supporting the write operation.

A project link must be set when creating work packages through this route.

When setting start date, finish date, and duration together, their correctness will be checked and a 422 error will be returned if one value does not match with the two others. You can make the server compute a value: set only two values in the request and the third one will be computed and returned in the response. For instance, when sending `{ "startDate": "2022-08-23", duration: "P2D" }`, the response will include `{ "dueDate": "2022-08-24" }`.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.work_package_model import WorkPackageModel
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
    api_instance = openproject_client.WorkPackagesApi(api_client)
    notify = True # bool | Indicates whether change notifications (e.g. via E-Mail) should be sent. Note that this controls notifications for all users interested in changes to the work package (e.g. watchers, author and assignee), not just the current user. (optional) (default to True)
    work_package_model = openproject_client.WorkPackageModel() # WorkPackageModel |  (optional)

    try:
        # Create Work Package
        api_response = api_instance.create_work_package(notify=notify, work_package_model=work_package_model)
        print("The response of WorkPackagesApi->create_work_package:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkPackagesApi->create_work_package: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **notify** | **bool**| Indicates whether change notifications (e.g. via E-Mail) should be sent. Note that this controls notifications for all users interested in changes to the work package (e.g. watchers, author and assignee), not just the current user. | [optional] [default to True]
 **work_package_model** | [**WorkPackageModel**](WorkPackageModel.md)|  | [optional] 

### Return type

[**WorkPackageModel**](WorkPackageModel.md)

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
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** add work packages  *Note that you will only receive this error, if you are at least allowed to see the corresponding project.* |  -  |
**404** | Returned if the project does not exist or the client does not have sufficient permissions to see it.  **Required permissions:** view project  *Note: A client without sufficient permissions shall not be able to test for the existence of a project. That&#39;s why a 404 is returned here, even if a 403 might be more appropriate.* |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |
**422** | Returned if:  * the client tries to write a read-only property  * a constraint for a property was violated  * a property was provided in an unreadable format |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_work_package_file_link**
> FileLinkCollectionReadModel create_work_package_file_link(id, file_link_collection_write_model=file_link_collection_write_model)

Creates file links.

Creates file links on a work package.

The request is interpreted as a bulk insert, where every element of the collection is validated separately. Each
element contains the origin meta data and a link to the storage, the file link is about to point to. The storage
link can be provided as a resource link with id or as the host url.

The file's id and name are considered mandatory information. The rest of the origin meta data SHOULD be provided
by the client. The _mimeType_ SHOULD be a standard mime type. An empty mime type will be handled as unknown. To link
a folder, the custom mime type `application/x-op-directory` MUST be used.

Up to 20 file links can be submitted at once.

If any element data is invalid, no file links will be created.

If a file link with matching origin id, work package, and storage already exists, then it will not create an
additional file link or update the meta data. Instead the information from the existing file link will be returned.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.file_link_collection_read_model import FileLinkCollectionReadModel
from openproject_client.models.file_link_collection_write_model import FileLinkCollectionWriteModel
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
    api_instance = openproject_client.WorkPackagesApi(api_client)
    id = 1337 # int | Work package id
    file_link_collection_write_model = {"_type":"Collection","_embedded":{"elements":[{"originData":{"id":5503,"name":"logo.png","mimeType":"image/png","size":433765,"createdAt":"2021-12-19T09:42:10.170Z","lastModifiedAt":"2021-12-20T14:00:13.987Z","createdByName":"Luke Skywalker","lastModifiedByName":"Anakin Skywalker"},"_links":{"storageUrl":{"href":"https://nextcloud.deathstar.rocks/"}}}]}} # FileLinkCollectionWriteModel |  (optional)

    try:
        # Creates file links.
        api_response = api_instance.create_work_package_file_link(id, file_link_collection_write_model=file_link_collection_write_model)
        print("The response of WorkPackagesApi->create_work_package_file_link:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkPackagesApi->create_work_package_file_link: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Work package id | 
 **file_link_collection_write_model** | [**FileLinkCollectionWriteModel**](FileLinkCollectionWriteModel.md)|  | [optional] 

### Return type

[**FileLinkCollectionReadModel**](FileLinkCollectionReadModel.md)

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
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** manage file links  *Note that you will only receive this error, if you are at least allowed to see the corresponding work package.* |  -  |
**404** | Returned if the work package does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view work package, view file links |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |
**422** | Occurs if the request body was correctly formatted, but some properties lead to errors in the validation process. This happens e.g. if the provided storage url is not available on the server. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_work_package_reminder**
> ReminderModel create_work_package_reminder(work_package_id, create_work_package_reminder_request)

Create a work package reminder

Creates a new reminder for the specified work package.

**Note:** A user can only have one **active** reminder at a time for a given work package.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.create_work_package_reminder_request import CreateWorkPackageReminderRequest
from openproject_client.models.reminder_model import ReminderModel
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
    api_instance = openproject_client.WorkPackagesApi(api_client)
    work_package_id = 1 # int | Work package id
    create_work_package_reminder_request = openproject_client.CreateWorkPackageReminderRequest() # CreateWorkPackageReminderRequest | 

    try:
        # Create a work package reminder
        api_response = api_instance.create_work_package_reminder(work_package_id, create_work_package_reminder_request)
        print("The response of WorkPackagesApi->create_work_package_reminder:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkPackagesApi->create_work_package_reminder: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **work_package_id** | **int**| Work package id | 
 **create_work_package_reminder_request** | [**CreateWorkPackageReminderRequest**](CreateWorkPackageReminderRequest.md)|  | 

### Return type

[**ReminderModel**](ReminderModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Reminder created successfully |  -  |
**404** | Returned if the work package does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view work package |  -  |
**409** | Returned if the user already has an active reminder for this work package.  **Error message**: You can only set one reminder at a time for a work package. Please delete or update the existing reminder. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_workspace_work_package**
> WorkPackageModel create_workspace_work_package(id, notify=notify, work_package_model=work_package_model)

Create work package in workspace

When calling this endpoint the client provides a single object, containing at least the properties and links that
are required, in the body. The required fields of a WorkPackage can be found in its schema, which is embedded in
the respective form. Note that it is only allowed to provide properties or links supporting the write operation.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.work_package_model import WorkPackageModel
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
    api_instance = openproject_client.WorkPackagesApi(api_client)
    id = 1 # int | Project id
    notify = True # bool | Indicates whether change notifications (e.g. via E-Mail) should be sent. Note that this controls notifications for all users interested in changes to the work package (e.g. watchers, author and assignee), not just the current user. (optional) (default to True)
    work_package_model = openproject_client.WorkPackageModel() # WorkPackageModel |  (optional)

    try:
        # Create work package in workspace
        api_response = api_instance.create_workspace_work_package(id, notify=notify, work_package_model=work_package_model)
        print("The response of WorkPackagesApi->create_workspace_work_package:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkPackagesApi->create_workspace_work_package: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Project id | 
 **notify** | **bool**| Indicates whether change notifications (e.g. via E-Mail) should be sent. Note that this controls notifications for all users interested in changes to the work package (e.g. watchers, author and assignee), not just the current user. | [optional] [default to True]
 **work_package_model** | [**WorkPackageModel**](WorkPackageModel.md)|  | [optional] 

### Return type

[**WorkPackageModel**](WorkPackageModel.md)

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
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** add work packages  *Note that you will only receive this error, if you are at least allowed to see the corresponding workspace.* |  -  |
**404** | Returned if the workspace does not exist or the client does not have sufficient permissions to see it.  **Required permissions:** view workspace  *Note: A client without sufficient permissions shall not be able to test for the existence of a workspace. That&#39;s why a 404 is returned here, even if a 403 might be more appropriate.* |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |
**422** | Returned if:  * the client tries to write a read-only property  * a constraint for a property was violated  * a property was provided in an unreadable format |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_work_package**
> delete_work_package(id)

Delete Work Package

Deletes the work package, as well as:

- all associated time entries
- its hierarchy of child work packages

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
    api_instance = openproject_client.WorkPackagesApi(api_client)
    id = 1 # int | Work package id

    try:
        # Delete Work Package
        api_instance.delete_work_package(id)
    except Exception as e:
        print("Exception when calling WorkPackagesApi->delete_work_package: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Work package id | 

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
**204** | Returned if the work package was deleted successfully.  Note that the response body is empty as of now. In future versions of the API a body *might* be returned along with an appropriate HTTP status. |  -  |
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** delete work package |  -  |
**404** | Returned if the work package does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view work package |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **form_create_work_package**
> WorkPackageFormModel form_create_work_package(work_package_write_model=work_package_write_model)

Form for creating a Work Package

When calling this endpoint, the client provides a single object containing the properties and links to be
created, in the body. The input is validated and a schema response is returned. If the validation errors of the
response is empty, the same payload can be used to create a work package.

Only the properties of the work package write model are allowed to set on a work package on creation.

When setting start date, finish date, and duration together, their correctness will be checked and a validation
error will be returned if one value does not match with the two others. You can make the server compute a value:
set only two values in the request and the third one will be computed and returned in the response. For instance,
when sending `{ "startDate": "2022-08-23", duration: "P2D" }`, the response will
include `{ "dueDate": "2022-08-24" }`.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.work_package_form_model import WorkPackageFormModel
from openproject_client.models.work_package_write_model import WorkPackageWriteModel
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
    api_instance = openproject_client.WorkPackagesApi(api_client)
    work_package_write_model = openproject_client.WorkPackageWriteModel() # WorkPackageWriteModel |  (optional)

    try:
        # Form for creating a Work Package
        api_response = api_instance.form_create_work_package(work_package_write_model=work_package_write_model)
        print("The response of WorkPackagesApi->form_create_work_package:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkPackagesApi->form_create_work_package: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **work_package_write_model** | [**WorkPackageWriteModel**](WorkPackageWriteModel.md)|  | [optional] 

### Return type

[**WorkPackageFormModel**](WorkPackageFormModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json, application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **form_create_work_package_in_project**
> WorkPackageFormModel form_create_work_package_in_project(id, work_package_write_model=work_package_write_model)

Form for creating Work Packages in a Project

This endpoint allows you to validation a new work package creation body in a specific project. It works similarly
to the `/api/v3/work_packages/form` endpoint, but already specifies the work package's project in the path, so that
it does not have to be defined in the request body.

This endpoint is deprecated and replaced by [`/api/v3/workspaces/{id}/work_packages/form`](https://www.openproject.org/docs/api/endpoints/work-packages/#form-for-creating-work-packages-in-a-workspace)

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.work_package_form_model import WorkPackageFormModel
from openproject_client.models.work_package_write_model import WorkPackageWriteModel
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
    api_instance = openproject_client.WorkPackagesApi(api_client)
    id = 1 # int | ID of the project in which the work package will be created
    work_package_write_model = openproject_client.WorkPackageWriteModel() # WorkPackageWriteModel |  (optional)

    try:
        # Form for creating Work Packages in a Project
        api_response = api_instance.form_create_work_package_in_project(id, work_package_write_model=work_package_write_model)
        print("The response of WorkPackagesApi->form_create_work_package_in_project:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkPackagesApi->form_create_work_package_in_project: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| ID of the project in which the work package will be created | 
 **work_package_write_model** | [**WorkPackageWriteModel**](WorkPackageWriteModel.md)|  | [optional] 

### Return type

[**WorkPackageFormModel**](WorkPackageFormModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json, application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **form_create_work_package_in_workspace**
> WorkPackageFormModel form_create_work_package_in_workspace(id, work_package_write_model=work_package_write_model)

Form for creating Work Packages in a Workspace

This endpoint allows you to validation a new work package creation body in a specific workspace. It works similarly
to the `/api/v3/work_packages/form` endpoint, but already specifies the work package's workspace in the path, so that
it does not have to be defined in the request body.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.work_package_form_model import WorkPackageFormModel
from openproject_client.models.work_package_write_model import WorkPackageWriteModel
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
    api_instance = openproject_client.WorkPackagesApi(api_client)
    id = 1 # int | ID of the workspace in which the work package will be created
    work_package_write_model = openproject_client.WorkPackageWriteModel() # WorkPackageWriteModel |  (optional)

    try:
        # Form for creating Work Packages in a Workspace
        api_response = api_instance.form_create_work_package_in_workspace(id, work_package_write_model=work_package_write_model)
        print("The response of WorkPackagesApi->form_create_work_package_in_workspace:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkPackagesApi->form_create_work_package_in_workspace: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| ID of the workspace in which the work package will be created | 
 **work_package_write_model** | [**WorkPackageWriteModel**](WorkPackageWriteModel.md)|  | [optional] 

### Return type

[**WorkPackageFormModel**](WorkPackageFormModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json, application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **form_edit_work_package**
> WorkPackageFormModel form_edit_work_package(id, work_package_write_model=work_package_write_model)

Form for editing a Work Package

When calling this endpoint, the client provides a single object containing the properties and links to be
edited, in the body. The input is validated and a schema response is returned. If the validation errors of the
response is empty, the same payload can be used to edit the work package.

Only the properties of the work package write model are allowed to set on a work package on editing.

When setting start date, finish date, and duration together, their correctness will be checked and a validation
error will be returned if one value does not match with the two others. You can make the server compute a value:
set only two values in the request and the third one will be computed and returned in the response. For instance,
when sending `{ "startDate": "2022-08-23", duration: "P2D" }`, the response will
include `{ "dueDate": "2022-08-24" }`.

**Custom Field Validation**  

Required custom fields are only validated when they are explicitly provided in the request body. If a custom field
is not included in the form request, it will not be validated, allowing clients to validate partial updates
without triggering validation errors for unrelated required custom fields.

To override this behavior and validate all required custom fields regardless of whether they are included in the
request, set `validateCustomFields` to `true` in the `_meta` object of the request body.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.work_package_form_model import WorkPackageFormModel
from openproject_client.models.work_package_write_model import WorkPackageWriteModel
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
    api_instance = openproject_client.WorkPackagesApi(api_client)
    id = 1 # int | ID of the work package being modified
    work_package_write_model = openproject_client.WorkPackageWriteModel() # WorkPackageWriteModel |  (optional)

    try:
        # Form for editing a Work Package
        api_response = api_instance.form_edit_work_package(id, work_package_write_model=work_package_write_model)
        print("The response of WorkPackagesApi->form_edit_work_package:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkPackagesApi->form_edit_work_package: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| ID of the work package being modified | 
 **work_package_write_model** | [**WorkPackageWriteModel**](WorkPackageWriteModel.md)|  | [optional] 

### Return type

[**WorkPackageFormModel**](WorkPackageFormModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json, application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**404** | Returned if the work package does not exist or the client does not have sufficient permissions to see it.   **Required permission:** view work package |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_project_work_package_collection**
> WorkPackagesModel get_project_work_package_collection(id, offset=offset, page_size=page_size, filters=filters, sort_by=sort_by, group_by=group_by, show_sums=show_sums, select=select)

Get work packages of project

Returns the collection of work packages that are related to the given project.
This endpoint is deprecated and replaced by [`/api/v3/workspaces/{id}/work_packages`](https://www.openproject.org/docs/api/endpoints/work-packages/#get-work-packages-of-workspace)

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.work_packages_model import WorkPackagesModel
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
    api_instance = openproject_client.WorkPackagesApi(api_client)
    id = 1 # int | Project id
    offset = 1 # int | Page number inside the requested collection. (optional) (default to 1)
    page_size = 25 # int | Number of elements to display per page. (optional)
    filters = '[{ "status_id": { "operator": "o", "values": null }}]' # str | JSON specifying filter conditions. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. If no filter is to be applied, the client should send an empty array (`[]`). (optional) (default to '[{ "status_id": { "operator": "o", "values": null }}]')
    sort_by = '[["id", "asc"]]' # str | JSON specifying sort criteria. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. (optional) (default to '[["id", "asc"]]')
    group_by = 'status' # str | The column to group by. (optional)
    show_sums = False # bool | Indicates whether properties should be summed up if they support it. (optional) (default to False)
    select = 'total,elements/subject,elements/id,self' # str | Comma separated list of properties to include. (optional)

    try:
        # Get work packages of project
        api_response = api_instance.get_project_work_package_collection(id, offset=offset, page_size=page_size, filters=filters, sort_by=sort_by, group_by=group_by, show_sums=show_sums, select=select)
        print("The response of WorkPackagesApi->get_project_work_package_collection:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkPackagesApi->get_project_work_package_collection: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Project id | 
 **offset** | **int**| Page number inside the requested collection. | [optional] [default to 1]
 **page_size** | **int**| Number of elements to display per page. | [optional] 
 **filters** | **str**| JSON specifying filter conditions. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. If no filter is to be applied, the client should send an empty array (&#x60;[]&#x60;). | [optional] [default to &#39;[{ &quot;status_id&quot;: { &quot;operator&quot;: &quot;o&quot;, &quot;values&quot;: null }}]&#39;]
 **sort_by** | **str**| JSON specifying sort criteria. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. | [optional] [default to &#39;[[&quot;id&quot;, &quot;asc&quot;]]&#39;]
 **group_by** | **str**| The column to group by. | [optional] 
 **show_sums** | **bool**| Indicates whether properties should be summed up if they support it. | [optional] [default to False]
 **select** | **str**| Comma separated list of properties to include. | [optional] 

### Return type

[**WorkPackagesModel**](WorkPackagesModel.md)

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
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** view work packages  *Note that you will only receive this error, if you are at least allowed to see the corresponding project.* |  -  |
**404** | Returned if the project does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view project |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_workspace_work_package_collection**
> WorkPackagesModel get_workspace_work_package_collection(id, offset=offset, page_size=page_size, filters=filters, sort_by=sort_by, group_by=group_by, show_sums=show_sums, select=select)

Get work packages of workspace

Returns the collection of work packages that are related to the given workspace.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.work_packages_model import WorkPackagesModel
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
    api_instance = openproject_client.WorkPackagesApi(api_client)
    id = 1 # int | Workspace id
    offset = 1 # int | Page number inside the requested collection. (optional) (default to 1)
    page_size = 25 # int | Number of elements to display per page. (optional)
    filters = '[{ "status_id": { "operator": "o", "values": null }}]' # str | JSON specifying filter conditions. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. If no filter is to be applied, the client should send an empty array (`[]`). (optional) (default to '[{ "status_id": { "operator": "o", "values": null }}]')
    sort_by = '[["id", "asc"]]' # str | JSON specifying sort criteria. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. (optional) (default to '[["id", "asc"]]')
    group_by = 'status' # str | The column to group by. (optional)
    show_sums = False # bool | Indicates whether properties should be summed up if they support it. (optional) (default to False)
    select = 'total,elements/subject,elements/id,self' # str | Comma separated list of properties to include. (optional)

    try:
        # Get work packages of workspace
        api_response = api_instance.get_workspace_work_package_collection(id, offset=offset, page_size=page_size, filters=filters, sort_by=sort_by, group_by=group_by, show_sums=show_sums, select=select)
        print("The response of WorkPackagesApi->get_workspace_work_package_collection:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkPackagesApi->get_workspace_work_package_collection: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Workspace id | 
 **offset** | **int**| Page number inside the requested collection. | [optional] [default to 1]
 **page_size** | **int**| Number of elements to display per page. | [optional] 
 **filters** | **str**| JSON specifying filter conditions. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. If no filter is to be applied, the client should send an empty array (&#x60;[]&#x60;). | [optional] [default to &#39;[{ &quot;status_id&quot;: { &quot;operator&quot;: &quot;o&quot;, &quot;values&quot;: null }}]&#39;]
 **sort_by** | **str**| JSON specifying sort criteria. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. | [optional] [default to &#39;[[&quot;id&quot;, &quot;asc&quot;]]&#39;]
 **group_by** | **str**| The column to group by. | [optional] 
 **show_sums** | **bool**| Indicates whether properties should be summed up if they support it. | [optional] [default to False]
 **select** | **str**| Comma separated list of properties to include. | [optional] 

### Return type

[**WorkPackagesModel**](WorkPackagesModel.md)

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
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** view work packages  *Note that you will only receive this error, if you are at least allowed to see the corresponding workspace.* |  -  |
**404** | Returned if the workspace does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view workspace |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_available_relation_candidates**
> object list_available_relation_candidates(id, page_size=page_size, filters=filters, query=query, type=type, sort_by=sort_by)

Available relation candidates



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
    api_instance = openproject_client.WorkPackagesApi(api_client)
    id = 1 # int | Project id
    page_size = 25 # int | Maximum number of candidates to list (default 10) (optional)
    filters = '[{ \"status_id\": { \"operator\": \"o\", \"values\": null } }]' # str | JSON specifying filter conditions. Accepts the same filters as the [work packages](https://www.openproject.org/docs/api/endpoints/work-packages/) endpoint. (optional)
    query = '\"rollout\"' # str | Shortcut for filtering by ID or subject (optional)
    type = '\"follows\"' # str | Type of relation to find candidates for (default \"relates\") (optional)
    sort_by = '[["id", "asc"]]' # str | JSON specifying sort criteria. Accepts the same sort criteria as the [work packages](https://www.openproject.org/docs/api/endpoints/work-packages/) endpoint. (optional) (default to '[["id", "asc"]]')

    try:
        # Available relation candidates
        api_response = api_instance.list_available_relation_candidates(id, page_size=page_size, filters=filters, query=query, type=type, sort_by=sort_by)
        print("The response of WorkPackagesApi->list_available_relation_candidates:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkPackagesApi->list_available_relation_candidates: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Project id | 
 **page_size** | **int**| Maximum number of candidates to list (default 10) | [optional] 
 **filters** | **str**| JSON specifying filter conditions. Accepts the same filters as the [work packages](https://www.openproject.org/docs/api/endpoints/work-packages/) endpoint. | [optional] 
 **query** | **str**| Shortcut for filtering by ID or subject | [optional] 
 **type** | **str**| Type of relation to find candidates for (default \&quot;relates\&quot;) | [optional] 
 **sort_by** | **str**| JSON specifying sort criteria. Accepts the same sort criteria as the [work packages](https://www.openproject.org/docs/api/endpoints/work-packages/) endpoint. | [optional] [default to &#39;[[&quot;id&quot;, &quot;asc&quot;]]&#39;]

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
**404** | Returned if the work package does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view work package |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_watchers**
> WatchersModel list_watchers(id)

List watchers



### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.watchers_model import WatchersModel
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
    api_instance = openproject_client.WorkPackagesApi(api_client)
    id = 1 # int | Work package id

    try:
        # List watchers
        api_response = api_instance.list_watchers(id)
        print("The response of WorkPackagesApi->list_watchers:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkPackagesApi->list_watchers: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Work package id | 

### Return type

[**WatchersModel**](WatchersModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** view work package watchers  *Note that you will only receive this error, if you are at least allowed to see the corresponding work package.* |  -  |
**404** | Returned if the work package does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view work package  *Note that you will effectively not be able to see the watchers of a work package without being able to see the work package.* |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_work_package_activities**
> object list_work_package_activities(id)

List work package activities



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
    api_instance = openproject_client.WorkPackagesApi(api_client)
    id = 1 # int | Work package id

    try:
        # List work package activities
        api_response = api_instance.list_work_package_activities(id)
        print("The response of WorkPackagesApi->list_work_package_activities:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkPackagesApi->list_work_package_activities: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Work package id | 

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
**404** | Returned if the work package does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view work package |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_work_package_file_links**
> FileLinkCollectionReadModel list_work_package_file_links(id, filters=filters)

Gets all file links of a work package

Gets all file links of a work package.

As a side effect, for every file link a request is sent to the storage's origin to fetch live data and patch
the file link's data before returning, as well as retrieving permissions of the user on this origin file. 

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.file_link_collection_read_model import FileLinkCollectionReadModel
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
    api_instance = openproject_client.WorkPackagesApi(api_client)
    id = 1337 # int | Work package id
    filters = '[{\"storage\":{\"operator\":\"=\",\"values\":[\"42\"]}}]' # str | JSON specifying filter conditions. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. The following filters are supported:  - storage (optional)

    try:
        # Gets all file links of a work package
        api_response = api_instance.list_work_package_file_links(id, filters=filters)
        print("The response of WorkPackagesApi->list_work_package_file_links:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkPackagesApi->list_work_package_file_links: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Work package id | 
 **filters** | **str**| JSON specifying filter conditions. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. The following filters are supported:  - storage | [optional] 

### Return type

[**FileLinkCollectionReadModel**](FileLinkCollectionReadModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** view file links  *Note that you will only receive this error, if you are at least allowed to see the corresponding work package.* |  -  |
**404** | Returned if the work package does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view work package |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_work_package_reminders**
> ListReminders200Response list_work_package_reminders(work_package_id)

List work package reminders

Gets a list of your upcoming reminders for this work package.

Only active reminders that belong to the current user are returned.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.list_reminders200_response import ListReminders200Response
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
    api_instance = openproject_client.WorkPackagesApi(api_client)
    work_package_id = 1 # int | Work package id

    try:
        # List work package reminders
        api_response = api_instance.list_work_package_reminders(work_package_id)
        print("The response of WorkPackagesApi->list_work_package_reminders:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkPackagesApi->list_work_package_reminders: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **work_package_id** | **int**| Work package id | 

### Return type

[**ListReminders200Response**](ListReminders200Response.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** view work packages for the project the work package is contained in. |  -  |
**404** | Returned if the work package does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view work package |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_work_package_schemas**
> list_work_package_schemas(filters)

List Work Package Schemas

List all work package schemas that match the given filters. This endpoint does not return a successful response,
if no filter is given.

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
    api_instance = openproject_client.WorkPackagesApi(api_client)
    filters = '[{ \"id\": { \"operator\": \"=\", \"values\": [\"12-1\", \"14-2\"] } }]' # str | JSON specifying filter conditions. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported filters are:  + id: The schema's id  Schema id has the form `project_id-work_package_type_id`.

    try:
        # List Work Package Schemas
        api_instance.list_work_package_schemas(filters)
    except Exception as e:
        print("Exception when calling WorkPackagesApi->list_work_package_schemas: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **filters** | **str**| JSON specifying filter conditions. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported filters are:  + id: The schema&#39;s id  Schema id has the form &#x60;project_id-work_package_type_id&#x60;. | 

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
**200** | OK |  -  |
**400** | Occurs when the client did not send a valid JSON object in the request body. |  -  |
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** View work packages in any project. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_work_packages**
> WorkPackagesModel list_work_packages(offset=offset, page_size=page_size, filters=filters, sort_by=sort_by, group_by=group_by, show_sums=show_sums, select=select, timestamps=timestamps)

List work packages

Returns a collection of work packages.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.work_packages_model import WorkPackagesModel
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
    api_instance = openproject_client.WorkPackagesApi(api_client)
    offset = 1 # int | Page number inside the requested collection. (optional) (default to 1)
    page_size = 25 # int | Number of elements to display per page. (optional)
    filters = '[{ "status_id": { "operator": "o", "values": null }}]' # str | JSON specifying filter conditions. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. If no filter is to be applied, the client should send an empty array (`[]`), otherwise a default filter is applied. A Currently supported filters are (there are additional filters added by modules):  - assigned_to - assignee_or_group - attachment_base - attachment_content - attachment_file_name - author - blocked - blocks - category - comment - created_at - custom_field - dates_interval - description - done_ratio - due_date - duplicated - duplicates - duration - estimated_hours - file_link_origin_id - follows - group - id - includes - linkable_to_storage_id - linkable_to_storage_url - manual_sort - milestone - only_subproject - parent - partof - precedes - principal_base - priority - project - relatable - relates - required - requires - responsible - role - search - start_date - status - storage_id - storage_url - subject - subject_or_id - subproject - type - typeahead - updated_at - version - watcher - work_package (optional) (default to '[{ "status_id": { "operator": "o", "values": null }}]')
    sort_by = '[["id", "asc"]]' # str | JSON specifying sort criteria. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. (optional) (default to '[["id", "asc"]]')
    group_by = 'status' # str | The column to group by. (optional)
    show_sums = False # bool | Indicates whether properties should be summed up if they support it. (optional) (default to False)
    select = 'total,elements/subject,elements/id,self' # str | Comma separated list of properties to include. (optional)
    timestamps = 'PT0S' # str | In order to perform a [baseline comparison](/docs/api/baseline-comparisons), you may provide one or several timestamps in ISO-8601 format as comma-separated list. The timestamps may be absolute or relative, such as ISO8601 dates, ISO8601 durations and the following relative date keywords: \"oneDayAgo@HH:MM+HH:MM\", \"lastWorkingDay@HH:MM+HH:MM\", \"oneWeekAgo@HH:MM+HH:MM\", \"oneMonthAgo@HH:MM+HH:MM\". The first \"HH:MM\" part represents the zero paded hours and minutes. The last \"+HH:MM\" part represents the timezone offset from UTC associated with the time, the offset can be positive or negative e.g.\"oneDayAgo@01:00+01:00\", \"oneDayAgo@01:00-01:00\".  Usually, the first timestamp is the baseline date, the last timestamp is the current date. Values older than 1 day are accepted only with valid Enterprise Token available. (optional) (default to 'PT0S')

    try:
        # List work packages
        api_response = api_instance.list_work_packages(offset=offset, page_size=page_size, filters=filters, sort_by=sort_by, group_by=group_by, show_sums=show_sums, select=select, timestamps=timestamps)
        print("The response of WorkPackagesApi->list_work_packages:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkPackagesApi->list_work_packages: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **offset** | **int**| Page number inside the requested collection. | [optional] [default to 1]
 **page_size** | **int**| Number of elements to display per page. | [optional] 
 **filters** | **str**| JSON specifying filter conditions. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. If no filter is to be applied, the client should send an empty array (&#x60;[]&#x60;), otherwise a default filter is applied. A Currently supported filters are (there are additional filters added by modules):  - assigned_to - assignee_or_group - attachment_base - attachment_content - attachment_file_name - author - blocked - blocks - category - comment - created_at - custom_field - dates_interval - description - done_ratio - due_date - duplicated - duplicates - duration - estimated_hours - file_link_origin_id - follows - group - id - includes - linkable_to_storage_id - linkable_to_storage_url - manual_sort - milestone - only_subproject - parent - partof - precedes - principal_base - priority - project - relatable - relates - required - requires - responsible - role - search - start_date - status - storage_id - storage_url - subject - subject_or_id - subproject - type - typeahead - updated_at - version - watcher - work_package | [optional] [default to &#39;[{ &quot;status_id&quot;: { &quot;operator&quot;: &quot;o&quot;, &quot;values&quot;: null }}]&#39;]
 **sort_by** | **str**| JSON specifying sort criteria. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. | [optional] [default to &#39;[[&quot;id&quot;, &quot;asc&quot;]]&#39;]
 **group_by** | **str**| The column to group by. | [optional] 
 **show_sums** | **bool**| Indicates whether properties should be summed up if they support it. | [optional] [default to False]
 **select** | **str**| Comma separated list of properties to include. | [optional] 
 **timestamps** | **str**| In order to perform a [baseline comparison](/docs/api/baseline-comparisons), you may provide one or several timestamps in ISO-8601 format as comma-separated list. The timestamps may be absolute or relative, such as ISO8601 dates, ISO8601 durations and the following relative date keywords: \&quot;oneDayAgo@HH:MM+HH:MM\&quot;, \&quot;lastWorkingDay@HH:MM+HH:MM\&quot;, \&quot;oneWeekAgo@HH:MM+HH:MM\&quot;, \&quot;oneMonthAgo@HH:MM+HH:MM\&quot;. The first \&quot;HH:MM\&quot; part represents the zero paded hours and minutes. The last \&quot;+HH:MM\&quot; part represents the timezone offset from UTC associated with the time, the offset can be positive or negative e.g.\&quot;oneDayAgo@01:00+01:00\&quot;, \&quot;oneDayAgo@01:00-01:00\&quot;.  Usually, the first timestamp is the baseline date, the last timestamp is the current date. Values older than 1 day are accepted only with valid Enterprise Token available. | [optional] [default to &#39;PT0S&#39;]

### Return type

[**WorkPackagesModel**](WorkPackagesModel.md)

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
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** view work packages (globally or in any project) |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **project_available_assignees**
> AvailableAssigneesModel project_available_assignees(id)

Project Available assignees

Gets a list of users that can be assigned to work packages in the given project.
This endpoint is deprecated and replaced by [`/api/v3/workspaces/{id}/available_assignees`](https://www.openproject.org/docs/api/endpoints/work-packages/#workspace-available-assignees)

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.available_assignees_model import AvailableAssigneesModel
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
    api_instance = openproject_client.WorkPackagesApi(api_client)
    id = 1 # int | Project id

    try:
        # Project Available assignees
        api_response = api_instance.project_available_assignees(id)
        print("The response of WorkPackagesApi->project_available_assignees:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkPackagesApi->project_available_assignees: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Project id | 

### Return type

[**AvailableAssigneesModel**](AvailableAssigneesModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** add work packages  *Note that you will only receive this error, if you are at least allowed to see the corresponding project.* |  -  |
**404** | Returned if the project does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view project |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **remove_watcher**
> remove_watcher(id, user_id)

Remove watcher

Removes the specified user from the list of watchers for the given work package.

If the request succeeds, the specified user is not watching the work package anymore.

*Note: This might also be the case, if the specified user did not watch the work package prior to the request.*

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
    api_instance = openproject_client.WorkPackagesApi(api_client)
    id = 1 # int | Work package id
    user_id = 1 # int | User id

    try:
        # Remove watcher
        api_instance.remove_watcher(id, user_id)
    except Exception as e:
        print("Exception when calling WorkPackagesApi->remove_watcher: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Work package id | 
 **user_id** | **int**| User id | 

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
**204** | No Content |  -  |
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** delete work package watchers  *Note that you will only receive this error, if you are at least allowed to see the corresponding work package.* |  -  |
**404** | Returned in one of the following cases:  Either the work package does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view work package  Or the specified user does not exist at all.  *Note that you will effectively not be able to change the watchers of a work package without being able to see the work package.* |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **revisions**
> object revisions(id)

Revisions

Gets a list of revisions that are linked to this work package, e.g., because it is referenced in the commit message of the revision.
Only linked revisions from repositories are shown if the user has the view changesets permission in the defining project.

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
    api_instance = openproject_client.WorkPackagesApi(api_client)
    id = 1 # int | Work package id

    try:
        # Revisions
        api_response = api_instance.revisions(id)
        print("The response of WorkPackagesApi->revisions:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkPackagesApi->revisions: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Work package id | 

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
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** view work packages for the project the work package is contained in.  *Note that you will only receive this error, if you are at least allowed to see the corresponding work package.* |  -  |
**404** | Returned if the work package does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view work package |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_work_package**
> WorkPackageModel update_work_package(id, notify=notify, work_package_patch_model=work_package_patch_model)

Update a Work Package

When calling this endpoint the client provides a single object, containing the properties and links that it wants
to change, in the body. Note that it is only allowed to provide properties or links supporting the **write**
operation.

Additionally to the fields the client wants to change, it is mandatory to provide the value of `lockVersion` which
was received by the `GET` request this change originates from.

The value of `lockVersion` is used to implement
[optimistic locking](https://en.wikipedia.org/wiki/Optimistic_concurrency_control).

**Custom Field Validation**  

Required custom fields are only validated when they are explicitly provided in the request body. If a custom field
is not included in the update request, it will not be validated. This enables clients to update
specific attributes independently without having to provide values for all required custom fields.

To override this behavior and validate all required custom fields regardless of whether they are included in the
request, set `validateCustomFields` to `true` in the `_meta` object of the request body.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.work_package_model import WorkPackageModel
from openproject_client.models.work_package_patch_model import WorkPackagePatchModel
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
    api_instance = openproject_client.WorkPackagesApi(api_client)
    id = 42 # int | Work package id
    notify = True # bool | Indicates whether change notifications should be sent. Note that this controls notifications for all users interested in changes to the work package (e.g. watchers, author and assignee), not just the current user. (optional) (default to True)
    work_package_patch_model = openproject_client.WorkPackagePatchModel() # WorkPackagePatchModel |  (optional)

    try:
        # Update a Work Package
        api_response = api_instance.update_work_package(id, notify=notify, work_package_patch_model=work_package_patch_model)
        print("The response of WorkPackagesApi->update_work_package:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkPackagesApi->update_work_package: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Work package id | 
 **notify** | **bool**| Indicates whether change notifications should be sent. Note that this controls notifications for all users interested in changes to the work package (e.g. watchers, author and assignee), not just the current user. | [optional] [default to True]
 **work_package_patch_model** | [**WorkPackagePatchModel**](WorkPackagePatchModel.md)|  | [optional] 

### Return type

[**WorkPackageModel**](WorkPackageModel.md)

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
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** edit work package, assign version, change work package status, manage subtasks or move work package |  -  |
**404** | Returned if the work package does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view work package |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**409** | Returned if the resource was changed since the client requested it. This is determined using the &#x60;lockVersion&#x60; property. |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |
**422** | Returned if:  - the client tries to modify a read-only property (&#x60;PropertyIsReadOnly&#x60;) - a constraint for a property was violated (&#x60;PropertyConstraintViolation&#x60;) - the client provides a link to an invalid resource (&#x60;ResourceTypeMismatch&#x60;) |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **view_work_package**
> WorkPackageModel view_work_package(id, timestamps=timestamps)

View Work Package

Returns the specified work package.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.work_package_model import WorkPackageModel
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
    api_instance = openproject_client.WorkPackagesApi(api_client)
    id = 1 # int | Work package id
    timestamps = 'PT0S' # str | In order to perform a [baseline comparison](/docs/api/baseline-comparisons) of the work-package attributes, you may provide one or several timestamps in ISO-8601 format as comma-separated list. The timestamps may be absolute or relative, such as ISO8601 dates, ISO8601 durations and the following relative date keywords: \"oneDayAgo@HH:MM+HH:MM\", \"lastWorkingDay@HH:MM+HH:MM\", \"oneWeekAgo@HH:MM+HH:MM\", \"oneMonthAgo@HH:MM+HH:MM\". The first \"HH:MM\" part represents the zero paded hours and minutes. The last \"+HH:MM\" part represents the timezone offset from UTC associated with the time, the offset can be positive or negative e.g.\"oneDayAgo@01:00+01:00\", \"oneDayAgo@01:00-01:00\".  Usually, the first timestamp is the baseline date, the last timestamp is the current date. Values older than 1 day are accepted only with valid Enterprise Token available. (optional) (default to 'PT0S')

    try:
        # View Work Package
        api_response = api_instance.view_work_package(id, timestamps=timestamps)
        print("The response of WorkPackagesApi->view_work_package:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkPackagesApi->view_work_package: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Work package id | 
 **timestamps** | **str**| In order to perform a [baseline comparison](/docs/api/baseline-comparisons) of the work-package attributes, you may provide one or several timestamps in ISO-8601 format as comma-separated list. The timestamps may be absolute or relative, such as ISO8601 dates, ISO8601 durations and the following relative date keywords: \&quot;oneDayAgo@HH:MM+HH:MM\&quot;, \&quot;lastWorkingDay@HH:MM+HH:MM\&quot;, \&quot;oneWeekAgo@HH:MM+HH:MM\&quot;, \&quot;oneMonthAgo@HH:MM+HH:MM\&quot;. The first \&quot;HH:MM\&quot; part represents the zero paded hours and minutes. The last \&quot;+HH:MM\&quot; part represents the timezone offset from UTC associated with the time, the offset can be positive or negative e.g.\&quot;oneDayAgo@01:00+01:00\&quot;, \&quot;oneDayAgo@01:00-01:00\&quot;.  Usually, the first timestamp is the baseline date, the last timestamp is the current date. Values older than 1 day are accepted only with valid Enterprise Token available. | [optional] [default to &#39;PT0S&#39;]

### Return type

[**WorkPackageModel**](WorkPackageModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**404** | Returned if the work package does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view work package |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **view_work_package_schema**
> view_work_package_schema(identifier)

View Work Package Schema



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
    api_instance = openproject_client.WorkPackagesApi(api_client)
    identifier = '12-13' # str | Identifier of the schema

    try:
        # View Work Package Schema
        api_instance.view_work_package_schema(identifier)
    except Exception as e:
        print("Exception when calling WorkPackagesApi->view_work_package_schema: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **identifier** | **str**| Identifier of the schema | 

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
**200** | OK |  -  |
**404** | Returned if the schema does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view work packages (on the project where this schema is used)  *Note: A client without sufficient permissions shall not be able to test for the existence of a project. That&#39;s why a 404 is returned here, even if a 403 might be more appropriate.* |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **work_package_available_assignees**
> AvailableAssigneesModel work_package_available_assignees(id)

Work Package Available assignees

Gets a list of users that can be assigned to the given work package.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.available_assignees_model import AvailableAssigneesModel
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
    api_instance = openproject_client.WorkPackagesApi(api_client)
    id = 1 # int | Work package id

    try:
        # Work Package Available assignees
        api_response = api_instance.work_package_available_assignees(id)
        print("The response of WorkPackagesApi->work_package_available_assignees:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkPackagesApi->work_package_available_assignees: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Work package id | 

### Return type

[**AvailableAssigneesModel**](AvailableAssigneesModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** edit work packages  *Note that you will only receive this error, if you are at least allowed to see the corresponding work package.* |  -  |
**404** | Returned if the work package does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view work packages |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **workspace_available_assignees**
> AvailableAssigneesModel workspace_available_assignees(id)

Workspace Available assignees

Gets a list of users that can be assigned to work packages in the given workspace.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.available_assignees_model import AvailableAssigneesModel
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
    api_instance = openproject_client.WorkPackagesApi(api_client)
    id = 1 # int | Workspace id

    try:
        # Workspace Available assignees
        api_response = api_instance.workspace_available_assignees(id)
        print("The response of WorkPackagesApi->workspace_available_assignees:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkPackagesApi->workspace_available_assignees: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Workspace id | 

### Return type

[**AvailableAssigneesModel**](AvailableAssigneesModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** add work packages  *Note that you will only receive this error, if you are at least allowed to see the corresponding workspace.* |  -  |
**404** | Returned if the workspace does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view workspace |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

