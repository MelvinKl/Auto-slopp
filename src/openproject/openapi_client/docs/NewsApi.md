# openproject_client.NewsApi

All URIs are relative to *https://openproject.melvin.beer*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_news**](NewsApi.md#create_news) | **POST** /api/v3/news | Create News
[**delete_news**](NewsApi.md#delete_news) | **DELETE** /api/v3/news/{id} | Delete news
[**list_news**](NewsApi.md#list_news) | **GET** /api/v3/news | List News
[**update_news**](NewsApi.md#update_news) | **PATCH** /api/v3/news/{id} | Update news
[**view_news**](NewsApi.md#view_news) | **GET** /api/v3/news/{id} | View news


# **create_news**
> NewsModel create_news(news_create_model=news_create_model)

Create News

Creates a news entry. Only administrators and users with "Manage news" permission in the given project are eligible.
When calling this endpoint the client provides a single object, containing at least the properties and links that are required, in the body.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.news_create_model import NewsCreateModel
from openproject_client.models.news_model import NewsModel
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
    api_instance = openproject_client.NewsApi(api_client)
    news_create_model = openproject_client.NewsCreateModel() # NewsCreateModel |  (optional)

    try:
        # Create News
        api_response = api_instance.create_news(news_create_model=news_create_model)
        print("The response of NewsApi->create_news:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling NewsApi->create_news: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **news_create_model** | [**NewsCreateModel**](NewsCreateModel.md)|  | [optional] 

### Return type

[**NewsModel**](NewsModel.md)

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
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** Administrator, Manage news permission in the project |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |
**422** | Returned if:  * the client tries to modify a read-only property (&#x60;PropertyIsReadOnly&#x60;)  * a constraint for a property was violated (&#x60;PropertyConstraintViolation&#x60;) |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_news**
> delete_news(id)

Delete news

Permanently deletes the specified news entry.

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
    api_instance = openproject_client.NewsApi(api_client)
    id = 1 # int | News id

    try:
        # Delete news
        api_instance.delete_news(id)
    except Exception as e:
        print("Exception when calling NewsApi->delete_news: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| News id | 

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
**202** | Returned if the news was deleted successfully.  Note that the response body is empty as of now. In future versions of the API a body *might* be returned, indicating the progress of deletion. |  -  |
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** Administrators and Manage news permission |  -  |
**404** | Returned if the news does not exist. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_news**
> object list_news(offset=offset, page_size=page_size, sort_by=sort_by, filters=filters)

List News

Lists news. The news returned depend on the provided parameters and also on the requesting user's permissions.

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
    api_instance = openproject_client.NewsApi(api_client)
    offset = 1 # int | Page number inside the requested collection. (optional) (default to 1)
    page_size = 25 # int | Number of elements to display per page. (optional)
    sort_by = '[[\"created_at\", \"asc\"]]' # str | JSON specifying sort criteria. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported sorts are:  + id: Sort by primary key  + created_at: Sort by news creation datetime (optional)
    filters = '[{ \"project_id\": { \"operator\": \"=\", \"values\": [\"1\", \"2\"] } }]' # str | JSON specifying filter conditions. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported filters are:  + project_id: Filter news by project (optional)

    try:
        # List News
        api_response = api_instance.list_news(offset=offset, page_size=page_size, sort_by=sort_by, filters=filters)
        print("The response of NewsApi->list_news:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling NewsApi->list_news: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **offset** | **int**| Page number inside the requested collection. | [optional] [default to 1]
 **page_size** | **int**| Number of elements to display per page. | [optional] 
 **sort_by** | **str**| JSON specifying sort criteria. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported sorts are:  + id: Sort by primary key  + created_at: Sort by news creation datetime | [optional] 
 **filters** | **str**| JSON specifying filter conditions. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported filters are:  + project_id: Filter news by project | [optional] 

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
**400** | Occurs when the client did not send a valid JSON object in the request body. |  -  |
**403** | Returned if the client is not logged in and login is required. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_news**
> NewsModel update_news(id, news_create_model=news_create_model)

Update news

Updates the news's writable attributes.
When calling this endpoint the client provides a single object, containing the properties and links to be updated, in the body.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.news_create_model import NewsCreateModel
from openproject_client.models.news_model import NewsModel
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
    api_instance = openproject_client.NewsApi(api_client)
    id = 1 # int | News id
    news_create_model = openproject_client.NewsCreateModel() # NewsCreateModel |  (optional)

    try:
        # Update news
        api_response = api_instance.update_news(id, news_create_model=news_create_model)
        print("The response of NewsApi->update_news:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling NewsApi->update_news: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| News id | 
 **news_create_model** | [**NewsCreateModel**](NewsCreateModel.md)|  | [optional] 

### Return type

[**NewsModel**](NewsModel.md)

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
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** Administrators, Manage news permission |  -  |
**404** | Returned if the news entry does not exist or if the API user does not have the necessary permissions to update it.  **Required permission:** Administrators, Manage news permission |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |
**422** | Returned if:  * the client tries to modify a read-only property (&#x60;PropertyIsReadOnly&#x60;)  * a constraint for a property was violated (&#x60;PropertyConstraintViolation&#x60;) |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **view_news**
> NewsModel view_news(id)

View news



### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.news_model import NewsModel
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
    api_instance = openproject_client.NewsApi(api_client)
    id = 1 # int | news id

    try:
        # View news
        api_response = api_instance.view_news(id)
        print("The response of NewsApi->view_news:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling NewsApi->view_news: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| news id | 

### Return type

[**NewsModel**](NewsModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**404** | Returned if the news does not exist or if the user does not have permission to view it.  **Required permission** being member of the project the news belongs to |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

