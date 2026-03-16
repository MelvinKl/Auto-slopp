# openproject_client.WikiPagesApi

All URIs are relative to *https://openproject.melvin.beer*

Method | HTTP request | Description
------------- | ------------- | -------------
[**view_wiki_page**](WikiPagesApi.md#view_wiki_page) | **GET** /api/v3/wiki_pages/{id} | View Wiki Page


# **view_wiki_page**
> WikiPageModel view_wiki_page(id)

View Wiki Page

Retrieve an individual wiki page as identified by the id parameter

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.wiki_page_model import WikiPageModel
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
    api_instance = openproject_client.WikiPagesApi(api_client)
    id = 1 # int | Wiki page identifier

    try:
        # View Wiki Page
        api_response = api_instance.view_wiki_page(id)
        print("The response of WikiPagesApi->view_wiki_page:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WikiPagesApi->view_wiki_page: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Wiki page identifier | 

### Return type

[**WikiPageModel**](WikiPageModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**404** | Returned if the wiki page does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view wiki page in the page&#39;s project |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

