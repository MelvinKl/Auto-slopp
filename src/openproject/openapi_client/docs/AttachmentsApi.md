# openproject_client.AttachmentsApi

All URIs are relative to *https://openproject.melvin.beer*

Method | HTTP request | Description
------------- | ------------- | -------------
[**add_attachment_to_meeting**](AttachmentsApi.md#add_attachment_to_meeting) | **POST** /api/v3/meetings/{id}/attachments | Add attachment to meeting
[**add_attachment_to_post**](AttachmentsApi.md#add_attachment_to_post) | **POST** /api/v3/posts/{id}/attachments | Add attachment to post
[**add_attachment_to_wiki_page**](AttachmentsApi.md#add_attachment_to_wiki_page) | **POST** /api/v3/wiki_pages/{id}/attachments | Add attachment to wiki page
[**create_activity_attachment**](AttachmentsApi.md#create_activity_attachment) | **POST** /api/v3/activities/{id}/attachments | Add attachment to activity
[**create_attachment**](AttachmentsApi.md#create_attachment) | **POST** /api/v3/attachments | Create Attachment
[**create_work_package_attachment**](AttachmentsApi.md#create_work_package_attachment) | **POST** /api/v3/work_packages/{id}/attachments | Create work package attachment
[**delete_attachment**](AttachmentsApi.md#delete_attachment) | **DELETE** /api/v3/attachments/{id} | Delete attachment
[**list_activity_attachments**](AttachmentsApi.md#list_activity_attachments) | **GET** /api/v3/activities/{id}/attachments | List attachments by activity
[**list_attachments_by_meeting**](AttachmentsApi.md#list_attachments_by_meeting) | **GET** /api/v3/meetings/{id}/attachments | List attachments by meeting
[**list_attachments_by_post**](AttachmentsApi.md#list_attachments_by_post) | **GET** /api/v3/posts/{id}/attachments | List attachments by post
[**list_attachments_by_wiki_page**](AttachmentsApi.md#list_attachments_by_wiki_page) | **GET** /api/v3/wiki_pages/{id}/attachments | List attachments by wiki page
[**list_work_package_attachments**](AttachmentsApi.md#list_work_package_attachments) | **GET** /api/v3/work_packages/{id}/attachments | List attachments by work package
[**view_attachment**](AttachmentsApi.md#view_attachment) | **GET** /api/v3/attachments/{id} | View attachment


# **add_attachment_to_meeting**
> add_attachment_to_meeting(id)

Add attachment to meeting

Adds an attachment with the meeting as its container.

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
    api_instance = openproject_client.AttachmentsApi(api_client)
    id = 1 # int | ID of the meeting to receive the attachment

    try:
        # Add attachment to meeting
        api_instance.add_attachment_to_meeting(id)
    except Exception as e:
        print("Exception when calling AttachmentsApi->add_attachment_to_meeting: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| ID of the meeting to receive the attachment | 

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
**200** | OK |  -  |
**400** | Returned if the client sends a not understandable request. Reasons include:  * Omitting one of the required parts (metadata and file)  * sending unparsable JSON in the metadata part |  -  |
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** edit meetings  *Note that you will only receive this error, if you are at least allowed to see the meeting* |  -  |
**404** | Returned if the meeting does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view meetings  *Note: A client without sufficient permissions shall not be able to test for the existence of a meeting That&#39;s why a 404 is returned here, even if a 403 might be more appropriate.* |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |
**422** | Returned if the client tries to send an invalid attachment. Reasons are:  * Omitting the file name (&#x60;fileName&#x60; property of metadata part)  * Sending a file that is too large |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_attachment_to_post**
> add_attachment_to_post(id)

Add attachment to post

Adds an attachment with the post as its container.

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
    api_instance = openproject_client.AttachmentsApi(api_client)
    id = 1 # int | ID of the post to receive the attachment

    try:
        # Add attachment to post
        api_instance.add_attachment_to_post(id)
    except Exception as e:
        print("Exception when calling AttachmentsApi->add_attachment_to_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| ID of the post to receive the attachment | 

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
**200** | OK |  -  |
**400** | Returned if the client sends a not understandable request. Reasons include:  * Omitting one of the required parts (metadata and file)  * sending unparsable JSON in the metadata part |  -  |
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** edit messages  *Note that you will only receive this error, if you are at least allowed to see the wiki page* |  -  |
**404** | Returned if the post does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view messages  *Note: A client without sufficient permissions shall not be able to test for the existence of a post. That&#39;s why a 404 is returned here, even if a 403 might be more appropriate.* |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |
**422** | Returned if the client tries to send an invalid attachment. Reasons are:  * Omitting the file name (&#x60;fileName&#x60; property of metadata part)  * Sending a file that is too large |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_attachment_to_wiki_page**
> add_attachment_to_wiki_page(id)

Add attachment to wiki page

Adds an attachment with the wiki page as its container.

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
    api_instance = openproject_client.AttachmentsApi(api_client)
    id = 1 # int | ID of the wiki page to receive the attachment

    try:
        # Add attachment to wiki page
        api_instance.add_attachment_to_wiki_page(id)
    except Exception as e:
        print("Exception when calling AttachmentsApi->add_attachment_to_wiki_page: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| ID of the wiki page to receive the attachment | 

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
**200** | OK |  -  |
**400** | Returned if the client sends a not understandable request. Reasons include:  * Omitting one of the required parts (metadata and file)  * sending unparsable JSON in the metadata part |  -  |
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** edit wiki pages  *Note that you will only receive this error, if you are at least allowed to see the wiki page* |  -  |
**404** | Returned if the wiki page does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view wiki pages  *Note: A client without sufficient permissions shall not be able to test for the existence of a wiki page That&#39;s why a 404 is returned here, even if a 403 might be more appropriate.* |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |
**422** | Returned if the client tries to send an invalid attachment. Reasons are:  * Omitting the file name (&#x60;fileName&#x60; property of metadata part)  * Sending a file that is too large |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_activity_attachment**
> AttachmentModel create_activity_attachment(id, metadata=metadata, file=file)

Add attachment to activity

Adds an attachment to the specified activity.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.attachment_model import AttachmentModel
from openproject_client.models.file_upload_form_metadata import FileUploadFormMetadata
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
    api_instance = openproject_client.AttachmentsApi(api_client)
    id = 1 # int | ID of the activity to receive the attachment
    metadata = openproject_client.FileUploadFormMetadata() # FileUploadFormMetadata |  (optional)
    file = None # bytearray |  (optional)

    try:
        # Add attachment to activity
        api_response = api_instance.create_activity_attachment(id, metadata=metadata, file=file)
        print("The response of AttachmentsApi->create_activity_attachment:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AttachmentsApi->create_activity_attachment: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| ID of the activity to receive the attachment | 
 **metadata** | [**FileUploadFormMetadata**](FileUploadFormMetadata.md)|  | [optional] 
 **file** | **bytearray**|  | [optional] 

### Return type

[**AttachmentModel**](AttachmentModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/hal+json, text/plain

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**400** | Returned if the client sends a not understandable request. Reasons include:  * Omitting one of the required parts (metadata and file)  * sending unparsable JSON in the metadata part |  -  |
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** view_work_packages or view_internal_comments (for internal comments)  *Note that you will only receive this error, if you are at least allowed to see the activity* |  -  |
**404** | Returned if the activity does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view_work_packages or view_internal_comments (for internal comments)  *Note: A client without sufficient permissions shall not be able to test for the existence of an activity. That&#39;s why a 404 is returned here, even if a 403 might be more appropriate.* |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |
**422** | Returned if the client tries to send an invalid attachment. Reasons are:  * Omitting the file name (&#x60;fileName&#x60; property of metadata part)  * Sending a file that is too large |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_attachment**
> AttachmentModel create_attachment()

Create Attachment

Clients can create attachments without a container first and attach them later on.
This is useful if the container does not exist at the time the attachment is uploaded.
After the upload, the client can then claim such containerless attachments for any resource eligible (e.g. WorkPackage) on subsequent requests.
The upload and the claiming *must* be done for the same user account. Attachments uploaded by another user cannot be claimed and
once claimed for a resource, they cannot be claimed by another.

The upload request must be of type `multipart/form-data` with exactly two parts.

The first part *must* be called `metadata`. Its content type is expected to be `application/json`,
the body *must* be a single JSON object, containing at least the `fileName` and optionally the attachments `description`.

The second part *must* be called `file`, its content type *should* match the mime type of the file.
The body *must* be the raw content of the file.
Note that a `filename` *must* be indicated in the `Content-Disposition` of this part, although it will be ignored.
Instead the `fileName` inside the JSON of the metadata part will be used.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.attachment_model import AttachmentModel
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
    api_instance = openproject_client.AttachmentsApi(api_client)

    try:
        # Create Attachment
        api_response = api_instance.create_attachment()
        print("The response of AttachmentsApi->create_attachment:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AttachmentsApi->create_attachment: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**AttachmentModel**](AttachmentModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json, text/plain

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**400** | Returned if the client sends a not understandable request. Reasons include:  * Omitting one of the required parts (metadata and file)  * sending unparsable JSON in the metadata part |  -  |
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** At least one permission in any project: edit work package, add work package, edit messages, edit wiki pages (plugins might extend this list) |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |
**422** | Returned if the client tries to send an invalid attachment. Reasons are:  * Omitting the file name (&#x60;fileName&#x60; property of metadata part)  * Sending a file that is too large |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_work_package_attachment**
> AttachmentModel create_work_package_attachment(id)

Create work package attachment

To add an attachment to a work package, a client needs to issue a request of type `multipart/form-data`
with exactly two parts.

The first part *must* be called `metadata`. Its content type is expected to be `application/json`,
the body *must* be a single JSON object, containing at least the `fileName` and optionally the attachments `description`.

The second part *must* be called `file`, its content type *should* match the mime type of the file.
The body *must* be the raw content of the file.
Note that a `filename` must be indicated in the `Content-Disposition` of this part, however it will be ignored.
Instead the `fileName` inside the JSON of the metadata part will be used.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.attachment_model import AttachmentModel
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
    api_instance = openproject_client.AttachmentsApi(api_client)
    id = 1 # int | ID of the work package to receive the attachment

    try:
        # Create work package attachment
        api_response = api_instance.create_work_package_attachment(id)
        print("The response of AttachmentsApi->create_work_package_attachment:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AttachmentsApi->create_work_package_attachment: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| ID of the work package to receive the attachment | 

### Return type

[**AttachmentModel**](AttachmentModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json, text/plain

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**400** | Returned if the client sends a not understandable request. Reasons include:  * Omitting one of the required parts (metadata and file)  * sending unparsable JSON in the metadata part |  -  |
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** edit work package or add work package  *Note that you will only receive this error, if you are at least allowed to see the work package.* |  -  |
**404** | Returned if the work package does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view work package  *Note: A client without sufficient permissions shall not be able to test for the existence of a work package. That&#39;s why a 404 is returned here, even if a 403 might be more appropriate.* |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |
**422** | Returned if the client tries to send an invalid attachment. Reasons are:  * Omitting the file name (&#x60;fileName&#x60; property of metadata part)  * Sending a file that is too large |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_attachment**
> delete_attachment(id)

Delete attachment

Permanently deletes the specified attachment.

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
    api_instance = openproject_client.AttachmentsApi(api_client)
    id = 1 # int | Attachment id

    try:
        # Delete attachment
        api_instance.delete_attachment(id)
    except Exception as e:
        print("Exception when calling AttachmentsApi->delete_attachment: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Attachment id | 

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
**204** | Returned if the attachment was deleted successfully.  Note that the response body is empty as of now. In future versions of the API a body *might* be returned along with an appropriate HTTP status. |  -  |
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** edit permission for the container of the attachment or being the author for attachments without container  *Note that you will only receive this error, if you are at least allowed to see the attachment.* |  -  |
**404** | Returned if the attachment does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view permission for the container of the attachment or being the author for attachments without container  *Note: A client without sufficient permissions shall not be able to test for the existence of an attachment. That&#39;s why a 404 is returned here, even if a 403 might be more appropriate.* |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_activity_attachments**
> AttachmentsModel list_activity_attachments(id)

List attachments by activity

List all attachments of a single activity.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.attachments_model import AttachmentsModel
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
    api_instance = openproject_client.AttachmentsApi(api_client)
    id = 1 # int | ID of the activity whose attachments will be listed

    try:
        # List attachments by activity
        api_response = api_instance.list_activity_attachments(id)
        print("The response of AttachmentsApi->list_activity_attachments:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AttachmentsApi->list_activity_attachments: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| ID of the activity whose attachments will be listed | 

### Return type

[**AttachmentsModel**](AttachmentsModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**404** | Returned if the activity does not exist or the client does not have sufficient permissions to see it.  **Required permission:**  - &#x60;view_work_packages&#x60; - for internal comments: &#x60;view_internal_comments&#x60;  *Note: A client without sufficient permissions shall not be able to test for the existence of an activity. That&#39;s why a 404 is returned here, even if a 403 might be more appropriate.* |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_attachments_by_meeting**
> AttachmentsModel list_attachments_by_meeting(id)

List attachments by meeting



### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.attachments_model import AttachmentsModel
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
    api_instance = openproject_client.AttachmentsApi(api_client)
    id = 1 # int | ID of the meeting whose attachments will be listed

    try:
        # List attachments by meeting
        api_response = api_instance.list_attachments_by_meeting(id)
        print("The response of AttachmentsApi->list_attachments_by_meeting:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AttachmentsApi->list_attachments_by_meeting: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| ID of the meeting whose attachments will be listed | 

### Return type

[**AttachmentsModel**](AttachmentsModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**404** | Returned if the meeting does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view meetings  *Note: A client without sufficient permissions shall not be able to test for the existence of a meeting. That&#39;s why a 404 is returned here, even if a 403 might be more appropriate.* |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_attachments_by_post**
> AttachmentsModel list_attachments_by_post(id)

List attachments by post



### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.attachments_model import AttachmentsModel
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
    api_instance = openproject_client.AttachmentsApi(api_client)
    id = 1 # int | ID of the post whose attachments will be listed

    try:
        # List attachments by post
        api_response = api_instance.list_attachments_by_post(id)
        print("The response of AttachmentsApi->list_attachments_by_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AttachmentsApi->list_attachments_by_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| ID of the post whose attachments will be listed | 

### Return type

[**AttachmentsModel**](AttachmentsModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**404** | Returned if the post does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view messages  *Note: A client without sufficient permissions shall not be able to test for the existence of a post. That&#39;s why a 404 is returned here, even if a 403 might be more appropriate.* |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_attachments_by_wiki_page**
> AttachmentsModel list_attachments_by_wiki_page(id)

List attachments by wiki page



### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.attachments_model import AttachmentsModel
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
    api_instance = openproject_client.AttachmentsApi(api_client)
    id = 1 # int | ID of the wiki page whose attachments will be listed

    try:
        # List attachments by wiki page
        api_response = api_instance.list_attachments_by_wiki_page(id)
        print("The response of AttachmentsApi->list_attachments_by_wiki_page:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AttachmentsApi->list_attachments_by_wiki_page: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| ID of the wiki page whose attachments will be listed | 

### Return type

[**AttachmentsModel**](AttachmentsModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**404** | Returned if the wiki page does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view wiki pages  *Note: A client without sufficient permissions shall not be able to test for the existence of a work package. That&#39;s why a 404 is returned here, even if a 403 might be more appropriate.* |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_work_package_attachments**
> AttachmentsModel list_work_package_attachments(id)

List attachments by work package



### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.attachments_model import AttachmentsModel
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
    api_instance = openproject_client.AttachmentsApi(api_client)
    id = 1 # int | ID of the work package whose attachments will be listed

    try:
        # List attachments by work package
        api_response = api_instance.list_work_package_attachments(id)
        print("The response of AttachmentsApi->list_work_package_attachments:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AttachmentsApi->list_work_package_attachments: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| ID of the work package whose attachments will be listed | 

### Return type

[**AttachmentsModel**](AttachmentsModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**404** | Returned if the work package does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view work package  *Note: A client without sufficient permissions shall not be able to test for the existence of a work package. That&#39;s why a 404 is returned here, even if a 403 might be more appropriate.* |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **view_attachment**
> AttachmentModel view_attachment(id)

View attachment



### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.attachment_model import AttachmentModel
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
    api_instance = openproject_client.AttachmentsApi(api_client)
    id = 1 # int | Attachment id

    try:
        # View attachment
        api_response = api_instance.view_attachment(id)
        print("The response of AttachmentsApi->view_attachment:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AttachmentsApi->view_attachment: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Attachment id | 

### Return type

[**AttachmentModel**](AttachmentModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**404** | Returned if the attachment does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view permission for the container of the attachment or being the author for attachments without container  *Note: A client without sufficient permissions shall not be able to test for the existence of an attachment. That&#39;s why a 404 is returned here, even if a 403 might be more appropriate.* |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

