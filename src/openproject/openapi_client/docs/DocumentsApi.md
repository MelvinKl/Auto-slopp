# openproject_client.DocumentsApi

All URIs are relative to *https://openproject.melvin.beer*

Method | HTTP request | Description
------------- | ------------- | -------------
[**list_documents**](DocumentsApi.md#list_documents) | **GET** /api/v3/documents | List Documents
[**update_document**](DocumentsApi.md#update_document) | **PATCH** /api/v3/documents/{id} | Update document
[**view_document**](DocumentsApi.md#view_document) | **GET** /api/v3/documents/{id} | View document


# **list_documents**
> object list_documents(offset=offset, page_size=page_size, sort_by=sort_by)

List Documents

The documents returned depend on the provided parameters and also on the requesting user's permissions.

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
    api_instance = openproject_client.DocumentsApi(api_client)
    offset = 1 # int | Page number inside the requested collection. (optional) (default to 1)
    page_size = 25 # int | Number of elements to display per page. (optional)
    sort_by = '[[\"created_at\", \"asc\"]]' # str | JSON specifying sort criteria. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported sorts are:  + id: Sort by primary key  + created_at: Sort by document creation datetime (optional)

    try:
        # List Documents
        api_response = api_instance.list_documents(offset=offset, page_size=page_size, sort_by=sort_by)
        print("The response of DocumentsApi->list_documents:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DocumentsApi->list_documents: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **offset** | **int**| Page number inside the requested collection. | [optional] [default to 1]
 **page_size** | **int**| Number of elements to display per page. | [optional] 
 **sort_by** | **str**| JSON specifying sort criteria. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. Currently supported sorts are:  + id: Sort by primary key  + created_at: Sort by document creation datetime | [optional] 

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
**400** | Returned if the client sends invalid request parameters e.g. filters |  -  |
**403** | Returned if the client is not logged in and login is required. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_document**
> DocumentModel update_document(id, update_document_request=update_document_request)

Update document

Updates a document's attributes.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.document_model import DocumentModel
from openproject_client.models.update_document_request import UpdateDocumentRequest
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
    api_instance = openproject_client.DocumentsApi(api_client)
    id = 1 # int | Document id
    update_document_request = {"title":"Updated document title","description":{"raw":"Updated description content"}} # UpdateDocumentRequest |  (optional)

    try:
        # Update document
        api_response = api_instance.update_document(id, update_document_request=update_document_request)
        print("The response of DocumentsApi->update_document:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DocumentsApi->update_document: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Document id | 
 **update_document_request** | [**UpdateDocumentRequest**](UpdateDocumentRequest.md)|  | [optional] 

### Return type

[**DocumentModel**](DocumentModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**400** | Returned if the request body is invalid. |  -  |
**403** | Returned if the user does not have permission to edit the document.  **Required permission** &#x60;manage documents&#x60; in the project the document belongs to |  -  |
**404** | Returned if the document does not exist or if the user does not have permission to view it.  **Required permission** &#x60;view documents&#x60; in the project the document belongs to |  -  |
**422** | Returned if the request body contains validation errors. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **view_document**
> DocumentModel view_document(id)

View document



### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.document_model import DocumentModel
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
    api_instance = openproject_client.DocumentsApi(api_client)
    id = 1 # int | Document id

    try:
        # View document
        api_response = api_instance.view_document(id)
        print("The response of DocumentsApi->view_document:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DocumentsApi->view_document: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Document id | 

### Return type

[**DocumentModel**](DocumentModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**404** | Returned if the document does not exist or if the user does not have permission to view it.  **Required permission** &#x60;view documents&#x60; in the project the document belongs to |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

