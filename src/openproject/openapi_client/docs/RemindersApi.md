# openproject_client.RemindersApi

All URIs are relative to *https://openproject.melvin.beer*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_work_package_reminder**](RemindersApi.md#create_work_package_reminder) | **POST** /api/v3/work_packages/{work_package_id}/reminders | Create a work package reminder
[**delete_reminder**](RemindersApi.md#delete_reminder) | **DELETE** /api/v3/reminders/{id} | Delete a reminder
[**list_reminders**](RemindersApi.md#list_reminders) | **GET** /api/v3/reminders | List all active reminders
[**list_work_package_reminders**](RemindersApi.md#list_work_package_reminders) | **GET** /api/v3/work_packages/{work_package_id}/reminders | List work package reminders
[**update_reminder**](RemindersApi.md#update_reminder) | **PATCH** /api/v3/reminders/{id} | Update a reminder


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
    api_instance = openproject_client.RemindersApi(api_client)
    work_package_id = 1 # int | Work package id
    create_work_package_reminder_request = openproject_client.CreateWorkPackageReminderRequest() # CreateWorkPackageReminderRequest | 

    try:
        # Create a work package reminder
        api_response = api_instance.create_work_package_reminder(work_package_id, create_work_package_reminder_request)
        print("The response of RemindersApi->create_work_package_reminder:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RemindersApi->create_work_package_reminder: %s\n" % e)
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

# **delete_reminder**
> delete_reminder(id)

Delete a reminder

Deletes an existing reminder.

A user can only delete their own active reminder.

**Required permission:** view work packages for the project the reminder is contained in.

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
    api_instance = openproject_client.RemindersApi(api_client)
    id = 1 # int | Reminder ID

    try:
        # Delete a reminder
        api_instance.delete_reminder(id)
    except Exception as e:
        print("Exception when calling RemindersApi->delete_reminder: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Reminder ID | 

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
**204** | Reminder deleted successfully |  -  |
**404** | Returned if the reminder does not exist or the client does not have sufficient permissions to see it. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_reminders**
> ListReminders200Response list_reminders()

List all active reminders

Gets a list of all active reminders for the user.

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
    api_instance = openproject_client.RemindersApi(api_client)

    try:
        # List all active reminders
        api_response = api_instance.list_reminders()
        print("The response of RemindersApi->list_reminders:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RemindersApi->list_reminders: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

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
    api_instance = openproject_client.RemindersApi(api_client)
    work_package_id = 1 # int | Work package id

    try:
        # List work package reminders
        api_response = api_instance.list_work_package_reminders(work_package_id)
        print("The response of RemindersApi->list_work_package_reminders:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RemindersApi->list_work_package_reminders: %s\n" % e)
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

# **update_reminder**
> ReminderModel update_reminder(id, update_reminder_request)

Update a reminder

Updates an existing reminder.

A user can only update their own active reminder.

**Required permission:** view work packages for the project the reminder is contained in.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.reminder_model import ReminderModel
from openproject_client.models.update_reminder_request import UpdateReminderRequest
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
    api_instance = openproject_client.RemindersApi(api_client)
    id = 1 # int | Reminder ID
    update_reminder_request = openproject_client.UpdateReminderRequest() # UpdateReminderRequest | 

    try:
        # Update a reminder
        api_response = api_instance.update_reminder(id, update_reminder_request)
        print("The response of RemindersApi->update_reminder:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RemindersApi->update_reminder: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Reminder ID | 
 **update_reminder_request** | [**UpdateReminderRequest**](UpdateReminderRequest.md)|  | 

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
**200** | Reminder updated successfully |  -  |
**404** | Returned if the reminder does not exist or the client does not have sufficient permissions to see it. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

