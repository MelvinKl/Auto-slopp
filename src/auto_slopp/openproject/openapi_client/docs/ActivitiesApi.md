# auto_slopp.openproject.openapi_client.ActivitiesApi

All URIs are relative to *https://openproject.melvin.beer*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_activity_attachment**](ActivitiesApi.md#create_activity_attachment) | **POST** /api/v3/activities/{id}/attachments | Add attachment to activity
[**get_activity**](ActivitiesApi.md#get_activity) | **GET** /api/v3/activities/{id} | Get an activity
[**list_activity_attachments**](ActivitiesApi.md#list_activity_attachments) | **GET** /api/v3/activities/{id}/attachments | List attachments by activity
[**list_activity_emoji_reactions**](ActivitiesApi.md#list_activity_emoji_reactions) | **GET** /api/v3/activities/{id}/emoji_reactions | List emoji reactions by activity
[**list_work_package_activities_emoji_reactions**](ActivitiesApi.md#list_work_package_activities_emoji_reactions) | **GET** /api/v3/work_packages/{id}/activities_emoji_reactions | List emoji reactions by work package activities
[**toggle_activity_emoji_reaction**](ActivitiesApi.md#toggle_activity_emoji_reaction) | **PATCH** /api/v3/activities/{id}/emoji_reactions | Toggle emoji reaction for an activity
[**update_activity**](ActivitiesApi.md#update_activity) | **PATCH** /api/v3/activities/{id} | Update activity


# **create_activity_attachment**
> AttachmentModel create_activity_attachment(id, metadata=metadata, file=file)

Add attachment to activity

Adds an attachment to the specified activity.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.attachment_model import AttachmentModel
from auto_slopp.openproject.openapi_client.models.file_upload_form_metadata import FileUploadFormMetadata
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
    api_instance = auto_slopp.openproject.openapi_client.ActivitiesApi(api_client)
    id = 1 # int | ID of the activity to receive the attachment
    metadata = auto_slopp.openproject.openapi_client.FileUploadFormMetadata() # FileUploadFormMetadata |  (optional)
    file = None # bytes |  (optional)

    try:
        # Add attachment to activity
        api_response = api_instance.create_activity_attachment(id, metadata=metadata, file=file)
        print("The response of ActivitiesApi->create_activity_attachment:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ActivitiesApi->create_activity_attachment: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| ID of the activity to receive the attachment | 
 **metadata** | [**FileUploadFormMetadata**](FileUploadFormMetadata.md)|  | [optional] 
 **file** | **bytes**|  | [optional] 

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

# **get_activity**
> ActivityModel get_activity(id)

Get an activity

Returns the requested activity resource identified by its unique id.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.activity_model import ActivityModel
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
    api_instance = auto_slopp.openproject.openapi_client.ActivitiesApi(api_client)
    id = 1 # int | Activity id

    try:
        # Get an activity
        api_response = api_instance.get_activity(id)
        print("The response of ActivitiesApi->get_activity:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ActivitiesApi->get_activity: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Activity id | 

### Return type

[**ActivityModel**](ActivityModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_activity_attachments**
> AttachmentsModel list_activity_attachments(id)

List attachments by activity

List all attachments of a single activity.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.attachments_model import AttachmentsModel
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
    api_instance = auto_slopp.openproject.openapi_client.ActivitiesApi(api_client)
    id = 1 # int | ID of the activity whose attachments will be listed

    try:
        # List attachments by activity
        api_response = api_instance.list_activity_attachments(id)
        print("The response of ActivitiesApi->list_activity_attachments:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ActivitiesApi->list_activity_attachments: %s\n" % e)
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

# **list_activity_emoji_reactions**
> EmojiReactionsModel list_activity_emoji_reactions(id)

List emoji reactions by activity

List all emoji reactions of a single activity.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.emoji_reactions_model import EmojiReactionsModel
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
    api_instance = auto_slopp.openproject.openapi_client.ActivitiesApi(api_client)
    id = 1 # int | ID of the activity whose emoji reactions will be listed

    try:
        # List emoji reactions by activity
        api_response = api_instance.list_activity_emoji_reactions(id)
        print("The response of ActivitiesApi->list_activity_emoji_reactions:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ActivitiesApi->list_activity_emoji_reactions: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| ID of the activity whose emoji reactions will be listed | 

### Return type

[**EmojiReactionsModel**](EmojiReactionsModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**404** | Returned if the activity does not exist or the client does not have sufficient permissions to see it.  **Required permission:** - &#x60;view_work_packages&#x60; - for internal comments: &#x60;view_internal_comments&#x60;  *Note: A client without sufficient permissions shall not be able to test for the existence of an activity. That&#39;s why a 404 is returned here, even if a 403 might be more appropriate.* |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_work_package_activities_emoji_reactions**
> EmojiReactionsModel list_work_package_activities_emoji_reactions(id)

List emoji reactions by work package activities

List all emoji reactions of all activities of a single work package.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.emoji_reactions_model import EmojiReactionsModel
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
    api_instance = auto_slopp.openproject.openapi_client.ActivitiesApi(api_client)
    id = 1 # int | ID of the work package whose activities' emoji reactions will be listed

    try:
        # List emoji reactions by work package activities
        api_response = api_instance.list_work_package_activities_emoji_reactions(id)
        print("The response of ActivitiesApi->list_work_package_activities_emoji_reactions:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ActivitiesApi->list_work_package_activities_emoji_reactions: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| ID of the work package whose activities&#39; emoji reactions will be listed | 

### Return type

[**EmojiReactionsModel**](EmojiReactionsModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**404** | Returned if the work package does not exist or the client does not have sufficient permissions to see it.  **Required permission:** - &#x60;view_work_packages&#x60; - for internal comments: &#x60;view_internal_comments&#x60;  *Note: A client without sufficient permissions shall not be able to test for the existence of a work package. That&#39;s why a 404 is returned here, even if a 403 might be more appropriate.* |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **toggle_activity_emoji_reaction**
> EmojiReactionModel toggle_activity_emoji_reaction(id, toggle_activity_emoji_reaction_request)

Toggle emoji reaction for an activity

Toggle an emoji reaction for a given activity. If the user has already reacted with the given emoji,
the reaction will be removed. Otherwise, a new reaction will be created.

**Note:** The response contains the complete collection of all emoji reactions for this activity.

**Required permission:**
- `add_work_package_comments`
- for internal comments: `add_internal_comments`

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.emoji_reaction_model import EmojiReactionModel
from auto_slopp.openproject.openapi_client.models.toggle_activity_emoji_reaction_request import ToggleActivityEmojiReactionRequest
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
    api_instance = auto_slopp.openproject.openapi_client.ActivitiesApi(api_client)
    id = 1 # int | ID of the activity to toggle emoji reaction for
    toggle_activity_emoji_reaction_request = auto_slopp.openproject.openapi_client.ToggleActivityEmojiReactionRequest() # ToggleActivityEmojiReactionRequest | 

    try:
        # Toggle emoji reaction for an activity
        api_response = api_instance.toggle_activity_emoji_reaction(id, toggle_activity_emoji_reaction_request)
        print("The response of ActivitiesApi->toggle_activity_emoji_reaction:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ActivitiesApi->toggle_activity_emoji_reaction: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| ID of the activity to toggle emoji reaction for | 
 **toggle_activity_emoji_reaction_request** | [**ToggleActivityEmojiReactionRequest**](ToggleActivityEmojiReactionRequest.md)|  | 

### Return type

[**EmojiReactionModel**](EmojiReactionModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: application/hal+json
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**400** | Returned if the request is invalid. For example, if the reaction is not valid. |  -  |
**403** | Returned if the client does not have sufficient permissions to toggle the emoji reaction for the activity. |  -  |
**404** | Returned if the activity does not exist or the client does not have sufficient permissions to see it. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_activity**
> ActivityModel update_activity(id, activity_comment_write_model=activity_comment_write_model)

Update activity

Updates an activity's comment and, on success, returns the updated activity.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.activity_comment_write_model import ActivityCommentWriteModel
from auto_slopp.openproject.openapi_client.models.activity_model import ActivityModel
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
    api_instance = auto_slopp.openproject.openapi_client.ActivitiesApi(api_client)
    id = 1 # int | Activity id
    activity_comment_write_model = auto_slopp.openproject.openapi_client.ActivityCommentWriteModel() # ActivityCommentWriteModel |  (optional)

    try:
        # Update activity
        api_response = api_instance.update_activity(id, activity_comment_write_model=activity_comment_write_model)
        print("The response of ActivitiesApi->update_activity:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ActivitiesApi->update_activity: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Activity id | 
 **activity_comment_write_model** | [**ActivityCommentWriteModel**](ActivityCommentWriteModel.md)|  | [optional] 

### Return type

[**ActivityModel**](ActivityModel.md)

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
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** edit journals |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |
**422** | Returned if the client tries to modify a read-only property. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

