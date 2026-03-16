# openproject_client.WorkScheduleApi

All URIs are relative to *https://openproject.melvin.beer*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_non_working_day**](WorkScheduleApi.md#create_non_working_day) | **POST** /api/v3/days/non_working | Creates a non-working day (NOT IMPLEMENTED)
[**delete_non_working_day**](WorkScheduleApi.md#delete_non_working_day) | **DELETE** /api/v3/days/non_working/{date} | Removes a non-working day (NOT IMPLEMENTED)
[**list_days**](WorkScheduleApi.md#list_days) | **GET** /api/v3/days | Lists days
[**list_non_working_days**](WorkScheduleApi.md#list_non_working_days) | **GET** /api/v3/days/non_working | Lists all non working days
[**list_week_days**](WorkScheduleApi.md#list_week_days) | **GET** /api/v3/days/week | Lists week days
[**update_non_working_day**](WorkScheduleApi.md#update_non_working_day) | **PATCH** /api/v3/days/non_working/{date} | Update a non-working day attributes (NOT IMPLEMENTED)
[**update_week_day**](WorkScheduleApi.md#update_week_day) | **PATCH** /api/v3/days/week/{day} | Update a week day attributes (NOT IMPLEMENTED)
[**update_week_days**](WorkScheduleApi.md#update_week_days) | **PATCH** /api/v3/days/week | Update week days (NOT IMPLEMENTED)
[**view_day**](WorkScheduleApi.md#view_day) | **GET** /api/v3/days/{date} | View day
[**view_non_working_day**](WorkScheduleApi.md#view_non_working_day) | **GET** /api/v3/days/non_working/{date} | View a non-working day
[**view_week_day**](WorkScheduleApi.md#view_week_day) | **GET** /api/v3/days/week/{day} | View a week day


# **create_non_working_day**
> NonWorkingDayModel create_non_working_day(non_working_day_model=non_working_day_model)

Creates a non-working day (NOT IMPLEMENTED)

**(NOT IMPLEMENTED)**
Marks a day as being a non-working day.

Note: creating a non-working day will not affect the start and finish dates
of work packages but will affect their duration.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.non_working_day_model import NonWorkingDayModel
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
    api_instance = openproject_client.WorkScheduleApi(api_client)
    non_working_day_model = {"_type":"NonWorkingDay","date":"2022-12-25","name":"Christmas"} # NonWorkingDayModel |  (optional)

    try:
        # Creates a non-working day (NOT IMPLEMENTED)
        api_response = api_instance.create_non_working_day(non_working_day_model=non_working_day_model)
        print("The response of WorkScheduleApi->create_non_working_day:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkScheduleApi->create_non_working_day: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **non_working_day_model** | [**NonWorkingDayModel**](NonWorkingDayModel.md)|  | [optional] 

### Return type

[**NonWorkingDayModel**](NonWorkingDayModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/hal+json, text/plain

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Non-working day created. |  -  |
**400** | Occurs when the client did not send a valid JSON object in the request body. |  -  |
**403** | Returned if the client does not have sufficient permissions. |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_non_working_day**
> delete_non_working_day(var_date)

Removes a non-working day (NOT IMPLEMENTED)

**(NOT IMPLEMENTED)**
Removes the non-working day at the given date.

Note: deleting a non-working day will not affect the start and finish dates
of work packages but will affect their duration.

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
    api_instance = openproject_client.WorkScheduleApi(api_client)
    var_date = '2022-05-06' # date | The date of the non-working day to view in ISO 8601 format.

    try:
        # Removes a non-working day (NOT IMPLEMENTED)
        api_instance.delete_non_working_day(var_date)
    except Exception as e:
        print("Exception when calling WorkScheduleApi->delete_non_working_day: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **var_date** | **date**| The date of the non-working day to view in ISO 8601 format. | 

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
**204** | No Content.  The operation succeeded. |  -  |
**400** | Occurs when the client did not send a valid JSON object in the request body. |  -  |
**404** | Returned if the given date is not a non-working day. |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_days**
> DayCollectionModel list_days(filters=filters)

Lists days

Lists days information for a given date interval.

All days from the beginning of current month to the end of following month
are returned by default.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.day_collection_model import DayCollectionModel
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
    api_instance = openproject_client.WorkScheduleApi(api_client)
    filters = '[{ \"date\": { \"operator\": \"<>d\", \"values\": [\"2022-05-02\",\"2022-05-26\"] } }, { \"working\": { \"operator\": \"=\", \"values\": [\"f\"] } }]' # str | JSON specifying filter conditions.  Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported filters are:  + date: the inclusive date interval to scope days to look up. When   unspecified, default is from the beginning of current month to the end   of following month.    Example: `{ \"date\": { \"operator\": \"<>d\", \"values\": [\"2022-05-02\",\"2022-05-26\"] } }`   would return days between May 5 and May 26 2022, inclusive.  + working: when `true`, returns only the working days. When `false`,   returns only the non-working days (weekend days and non-working days).   When unspecified, returns both working and non-working days.    Example: `{ \"working\": { \"operator\": \"=\", \"values\": [\"t\"] } }`   would exclude non-working days from the response. (optional)

    try:
        # Lists days
        api_response = api_instance.list_days(filters=filters)
        print("The response of WorkScheduleApi->list_days:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkScheduleApi->list_days: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **filters** | **str**| JSON specifying filter conditions.  Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported filters are:  + date: the inclusive date interval to scope days to look up. When   unspecified, default is from the beginning of current month to the end   of following month.    Example: &#x60;{ \&quot;date\&quot;: { \&quot;operator\&quot;: \&quot;&lt;&gt;d\&quot;, \&quot;values\&quot;: [\&quot;2022-05-02\&quot;,\&quot;2022-05-26\&quot;] } }&#x60;   would return days between May 5 and May 26 2022, inclusive.  + working: when &#x60;true&#x60;, returns only the working days. When &#x60;false&#x60;,   returns only the non-working days (weekend days and non-working days).   When unspecified, returns both working and non-working days.    Example: &#x60;{ \&quot;working\&quot;: { \&quot;operator\&quot;: \&quot;&#x3D;\&quot;, \&quot;values\&quot;: [\&quot;t\&quot;] } }&#x60;   would exclude non-working days from the response. | [optional] 

### Return type

[**DayCollectionModel**](DayCollectionModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json, text/plain

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**400** | Occurs when the client did not send a valid JSON object in the request body. |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_non_working_days**
> NonWorkingDayCollectionModel list_non_working_days(filters=filters)

Lists all non working days

Lists all one-time non working days, such as holidays.
It does not lists the non working weekdays, such as each Saturday, Sunday.
For listing the weekends, the `/api/v3/days` endpoint should be used.

All days from current year are returned by default.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.non_working_day_collection_model import NonWorkingDayCollectionModel
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
    api_instance = openproject_client.WorkScheduleApi(api_client)
    filters = '[{ \"date\": { \"operator\": \"<>d\", \"values\": [\"2022-05-02\",\"2022-05-26\"] } }]' # str | JSON specifying filter conditions.  Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported filters are:  + date: the inclusive date interval to scope days to look up. When   unspecified, default is from the beginning to the end of current year.    Example: `{ \"date\": { \"operator\": \"<>d\", \"values\": [\"2022-05-02\",\"2022-05-26\"] } }`   would return days between May 5 and May 26 2022, inclusive. (optional)

    try:
        # Lists all non working days
        api_response = api_instance.list_non_working_days(filters=filters)
        print("The response of WorkScheduleApi->list_non_working_days:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkScheduleApi->list_non_working_days: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **filters** | **str**| JSON specifying filter conditions.  Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported filters are:  + date: the inclusive date interval to scope days to look up. When   unspecified, default is from the beginning to the end of current year.    Example: &#x60;{ \&quot;date\&quot;: { \&quot;operator\&quot;: \&quot;&lt;&gt;d\&quot;, \&quot;values\&quot;: [\&quot;2022-05-02\&quot;,\&quot;2022-05-26\&quot;] } }&#x60;   would return days between May 5 and May 26 2022, inclusive. | [optional] 

### Return type

[**NonWorkingDayCollectionModel**](NonWorkingDayCollectionModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json, text/plain

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**400** | Occurs when the client did not send a valid JSON object in the request body. |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_week_days**
> WeekDayCollectionModel list_week_days()

Lists week days

Lists week days with work schedule information.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.week_day_collection_model import WeekDayCollectionModel
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
    api_instance = openproject_client.WorkScheduleApi(api_client)

    try:
        # Lists week days
        api_response = api_instance.list_week_days()
        print("The response of WorkScheduleApi->list_week_days:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkScheduleApi->list_week_days: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**WeekDayCollectionModel**](WeekDayCollectionModel.md)

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_non_working_day**
> NonWorkingDayModel update_non_working_day(var_date, non_working_day_model=non_working_day_model)

Update a non-working day attributes (NOT IMPLEMENTED)

**(NOT IMPLEMENTED)**
Update the non-working day information for a given date.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.non_working_day_model import NonWorkingDayModel
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
    api_instance = openproject_client.WorkScheduleApi(api_client)
    var_date = '2022-05-06' # date | The date of the non-working day to view in ISO 8601 format.
    non_working_day_model = {"_type":"NonWorkingDay","date":"2022-05-01","name":"Labour day"} # NonWorkingDayModel |  (optional)

    try:
        # Update a non-working day attributes (NOT IMPLEMENTED)
        api_response = api_instance.update_non_working_day(var_date, non_working_day_model=non_working_day_model)
        print("The response of WorkScheduleApi->update_non_working_day:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkScheduleApi->update_non_working_day: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **var_date** | **date**| The date of the non-working day to view in ISO 8601 format. | 
 **non_working_day_model** | [**NonWorkingDayModel**](NonWorkingDayModel.md)|  | [optional] 

### Return type

[**NonWorkingDayModel**](NonWorkingDayModel.md)

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
**404** | Returned if the given date is not a non-working day. |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_week_day**
> WeekDayModel update_week_day(day, week_day_write_model=week_day_write_model)

Update a week day attributes (NOT IMPLEMENTED)

**(NOT IMPLEMENTED)**
Makes a week day a working or non-working day.

Note: changing a week day working attribute will not affect the start and
finish dates of work packages but will affect their duration attribute.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.week_day_model import WeekDayModel
from openproject_client.models.week_day_write_model import WeekDayWriteModel
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
    api_instance = openproject_client.WorkScheduleApi(api_client)
    day = 56 # int | The week day from 1 to 7. 1 is Monday. 7 is Sunday.
    week_day_write_model = {"_type":"WeekDay","working":false} # WeekDayWriteModel |  (optional)

    try:
        # Update a week day attributes (NOT IMPLEMENTED)
        api_response = api_instance.update_week_day(day, week_day_write_model=week_day_write_model)
        print("The response of WorkScheduleApi->update_week_day:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkScheduleApi->update_week_day: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **day** | **int**| The week day from 1 to 7. 1 is Monday. 7 is Sunday. | 
 **week_day_write_model** | [**WeekDayWriteModel**](WeekDayWriteModel.md)|  | [optional] 

### Return type

[**WeekDayModel**](WeekDayModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/hal+json, text/plain

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Update succeeded.  Response will include the week day with updated attributes. |  -  |
**400** | Occurs when the client did not send a valid JSON object in the request body. |  -  |
**403** | Returned if the client does not have sufficient permissions. |  -  |
**404** | Returned if the day is out of the 1-7 range. |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_week_days**
> WeekDayCollectionModel update_week_days(week_day_collection_write_model=week_day_collection_write_model)

Update week days (NOT IMPLEMENTED)

**(NOT IMPLEMENTED)**
Update multiple week days with work schedule information.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.week_day_collection_model import WeekDayCollectionModel
from openproject_client.models.week_day_collection_write_model import WeekDayCollectionWriteModel
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
    api_instance = openproject_client.WorkScheduleApi(api_client)
    week_day_collection_write_model = openproject_client.WeekDayCollectionWriteModel() # WeekDayCollectionWriteModel |  (optional)

    try:
        # Update week days (NOT IMPLEMENTED)
        api_response = api_instance.update_week_days(week_day_collection_write_model=week_day_collection_write_model)
        print("The response of WorkScheduleApi->update_week_days:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkScheduleApi->update_week_days: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **week_day_collection_write_model** | [**WeekDayCollectionWriteModel**](WeekDayCollectionWriteModel.md)|  | [optional] 

### Return type

[**WeekDayCollectionModel**](WeekDayCollectionModel.md)

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
**404** | Returned if a week day resource can not be found. |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **view_day**
> DayModel view_day(var_date)

View day

View the day information for a given date.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.day_model import DayModel
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
    api_instance = openproject_client.WorkScheduleApi(api_client)
    var_date = '2022-05-06' # date | The date of the non-working day to view in ISO 8601 format.

    try:
        # View day
        api_response = api_instance.view_day(var_date)
        print("The response of WorkScheduleApi->view_day:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkScheduleApi->view_day: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **var_date** | **date**| The date of the non-working day to view in ISO 8601 format. | 

### Return type

[**DayModel**](DayModel.md)

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **view_non_working_day**
> NonWorkingDayModel view_non_working_day(var_date)

View a non-working day

Returns the non-working day information for a given date.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.non_working_day_model import NonWorkingDayModel
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
    api_instance = openproject_client.WorkScheduleApi(api_client)
    var_date = '2022-05-06' # date | The date of the non-working day to view in ISO 8601 format.

    try:
        # View a non-working day
        api_response = api_instance.view_non_working_day(var_date)
        print("The response of WorkScheduleApi->view_non_working_day:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkScheduleApi->view_non_working_day: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **var_date** | **date**| The date of the non-working day to view in ISO 8601 format. | 

### Return type

[**NonWorkingDayModel**](NonWorkingDayModel.md)

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
**404** | Returned if the given date is not a non-working day. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **view_week_day**
> WeekDayModel view_week_day(day)

View a week day

View a week day and its attributes.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.week_day_model import WeekDayModel
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
    api_instance = openproject_client.WorkScheduleApi(api_client)
    day = 56 # int | The week day from 1 to 7. 1 is Monday. 7 is Sunday.

    try:
        # View a week day
        api_response = api_instance.view_week_day(day)
        print("The response of WorkScheduleApi->view_week_day:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkScheduleApi->view_week_day: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **day** | **int**| The week day from 1 to 7. 1 is Monday. 7 is Sunday. | 

### Return type

[**WeekDayModel**](WeekDayModel.md)

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
**404** | Returned if the day is out of the 1-7 range. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

