# auto_slopp.openproject.openapi_client.PreviewingApi

All URIs are relative to *https://openproject.melvin.beer*

Method | HTTP request | Description
------------- | ------------- | -------------
[**preview_markdown_document**](PreviewingApi.md#preview_markdown_document) | **POST** /api/v3/render/markdown | Preview Markdown document
[**preview_plain_document**](PreviewingApi.md#preview_plain_document) | **POST** /api/v3/render/plain | Preview plain document


# **preview_markdown_document**
> str preview_markdown_document(context=context)

Preview Markdown document



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
    api_instance = auto_slopp.openproject.openapi_client.PreviewingApi(api_client)
    context = '/api/v3/work_packages/42' # str | API-Link to the context in which the rendering occurs, for example a specific work package.  If left out only context-agnostic rendering takes place. Please note that OpenProject features markdown-extensions on top of the extensions GitHub Flavored Markdown (gfm) already provides that can only work given a context (e.g. display attached images).  **Supported contexts:**  * `/api/v3/work_packages/{id}` - an existing work package (optional)

    try:
        # Preview Markdown document
        api_response = api_instance.preview_markdown_document(context=context)
        print("The response of PreviewingApi->preview_markdown_document:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PreviewingApi->preview_markdown_document: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **context** | **str**| API-Link to the context in which the rendering occurs, for example a specific work package.  If left out only context-agnostic rendering takes place. Please note that OpenProject features markdown-extensions on top of the extensions GitHub Flavored Markdown (gfm) already provides that can only work given a context (e.g. display attached images).  **Supported contexts:**  * &#x60;/api/v3/work_packages/{id}&#x60; - an existing work package | [optional] 

### Return type

**str**

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/html, application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**400** | Returned if the context passed by the client is not valid (e.g. unknown).  Note that this response will also occur when the requesting user is not allowed to see the context resource (e.g. limited work package visibility). |  -  |
**415** | Returned if the Content-Type indicated in the request is not &#x60;text/plain&#x60;. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **preview_plain_document**
> str preview_plain_document()

Preview plain document



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
    api_instance = auto_slopp.openproject.openapi_client.PreviewingApi(api_client)

    try:
        # Preview plain document
        api_response = api_instance.preview_plain_document()
        print("The response of PreviewingApi->preview_plain_document:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PreviewingApi->preview_plain_document: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

**str**

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/html, application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**415** | Returned if the Content-Type indicated in the request is not &#x60;text/plain&#x60;. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

