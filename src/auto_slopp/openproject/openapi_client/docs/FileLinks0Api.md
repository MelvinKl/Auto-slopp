# auto_slopp.openproject.openapi_client.FileLinksApi

All URIs are relative to *https://openproject.melvin.beer*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_storage**](FileLinksApi.md#create_storage) | **POST** /api/v3/storages | Creates a storage.
[**create_storage_folder**](FileLinksApi.md#create_storage_folder) | **POST** /api/v3/storages/{id}/folders | Creation of a new folder
[**create_storage_oauth_credentials**](FileLinksApi.md#create_storage_oauth_credentials) | **POST** /api/v3/storages/{id}/oauth_client_credentials | Creates an oauth client credentials object for a storage.
[**create_work_package_file_link**](FileLinksApi.md#create_work_package_file_link) | **POST** /api/v3/work_packages/{id}/file_links | Creates file links.
[**delete_file_link**](FileLinksApi.md#delete_file_link) | **DELETE** /api/v3/file_links/{id} | Removes a file link.
[**delete_storage**](FileLinksApi.md#delete_storage) | **DELETE** /api/v3/storages/{id} | Delete a storage
[**download_file_link**](FileLinksApi.md#download_file_link) | **GET** /api/v3/file_links/{id}/download | Creates a download uri of the linked file.
[**get_storage**](FileLinksApi.md#get_storage) | **GET** /api/v3/storages/{id} | Get a storage
[**get_storage_files**](FileLinksApi.md#get_storage_files) | **GET** /api/v3/storages/{id}/files | Gets files of a storage.
[**list_storages**](FileLinksApi.md#list_storages) | **GET** /api/v3/storages | Get Storages
[**list_work_package_file_links**](FileLinksApi.md#list_work_package_file_links) | **GET** /api/v3/work_packages/{id}/file_links | Gets all file links of a work package
[**open_file_link**](FileLinksApi.md#open_file_link) | **GET** /api/v3/file_links/{id}/open | Creates an opening uri of the linked file.
[**prepare_storage_file_upload**](FileLinksApi.md#prepare_storage_file_upload) | **POST** /api/v3/storages/{id}/files/prepare_upload | Preparation of a direct upload of a file to the given storage.
[**update_storage**](FileLinksApi.md#update_storage) | **PATCH** /api/v3/storages/{id} | Update a storage
[**view_file_link**](FileLinksApi.md#view_file_link) | **GET** /api/v3/file_links/{id} | Gets a file link.


# **create_storage**
> StorageReadModel create_storage(storage_write_model=storage_write_model)

Creates a storage.

Creates a storage resource. When creating a storage, a confidential OAuth 2 provider application is created
automatically. The oauth client id and secret of the created OAuth application are returned in the response.

**IMPORTANT:** This is the only time, the oauth client secret is visible to the consumer. After that, the secret is
hidden.

To update the storage with OAuth client credentials, which enable the storage resource to behave as an OAuth 2
client against an external OAuth 2 provider application, another request must be made to create those, see
`POST /api/v3/storages/{id}/oauth_client_credentials`.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.storage_read_model import StorageReadModel
from auto_slopp.openproject.openapi_client.models.storage_write_model import StorageWriteModel
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
    api_instance = auto_slopp.openproject.openapi_client.FileLinksApi(api_client)
    storage_write_model = auto_slopp.openproject.openapi_client.StorageWriteModel() # StorageWriteModel |  (optional)

    try:
        # Creates a storage.
        api_response = api_instance.create_storage(storage_write_model=storage_write_model)
        print("The response of FileLinksApi->create_storage:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FileLinksApi->create_storage: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **storage_write_model** | [**StorageWriteModel**](StorageWriteModel.md)|  | [optional] 

### Return type

[**StorageReadModel**](StorageReadModel.md)

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
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** Depends on the page the grid is defined for. |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |
**422** | Returned if:  * a constraint for a property was violated (&#x60;PropertyConstraintViolation&#x60;) |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_storage_folder**
> StorageFileModel create_storage_folder(id, storage_folder_write_model=storage_folder_write_model)

Creation of a new folder

Creates a new folder under the given parent

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.storage_file_model import StorageFileModel
from auto_slopp.openproject.openapi_client.models.storage_folder_write_model import StorageFolderWriteModel
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
    api_instance = auto_slopp.openproject.openapi_client.FileLinksApi(api_client)
    id = 1337 # int | Storage id
    storage_folder_write_model = auto_slopp.openproject.openapi_client.StorageFolderWriteModel() # StorageFolderWriteModel |  (optional)

    try:
        # Creation of a new folder
        api_response = api_instance.create_storage_folder(id, storage_folder_write_model=storage_folder_write_model)
        print("The response of FileLinksApi->create_storage_folder:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FileLinksApi->create_storage_folder: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Storage id | 
 **storage_folder_write_model** | [**StorageFolderWriteModel**](StorageFolderWriteModel.md)|  | [optional] 

### Return type

[**StorageFileModel**](StorageFileModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Created |  -  |
**400** | Returned if the request is missing a required parameter. |  -  |
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** manage file links |  -  |
**404** | Returned if the storage does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view file links |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_storage_oauth_credentials**
> StorageReadModel create_storage_oauth_credentials(id, o_auth_client_credentials_write_model=o_auth_client_credentials_write_model)

Creates an oauth client credentials object for a storage.

Inserts the OAuth 2 credentials into the storage, to allow the storage to act as an OAuth 2 client. Calling this
endpoint on a storage that already contains OAuth 2 client credentials will replace them.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.o_auth_client_credentials_write_model import OAuthClientCredentialsWriteModel
from auto_slopp.openproject.openapi_client.models.storage_read_model import StorageReadModel
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
    api_instance = auto_slopp.openproject.openapi_client.FileLinksApi(api_client)
    id = 1337 # int | Storage id
    o_auth_client_credentials_write_model = auto_slopp.openproject.openapi_client.OAuthClientCredentialsWriteModel() # OAuthClientCredentialsWriteModel |  (optional)

    try:
        # Creates an oauth client credentials object for a storage.
        api_response = api_instance.create_storage_oauth_credentials(id, o_auth_client_credentials_write_model=o_auth_client_credentials_write_model)
        print("The response of FileLinksApi->create_storage_oauth_credentials:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FileLinksApi->create_storage_oauth_credentials: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Storage id | 
 **o_auth_client_credentials_write_model** | [**OAuthClientCredentialsWriteModel**](OAuthClientCredentialsWriteModel.md)|  | [optional] 

### Return type

[**StorageReadModel**](StorageReadModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Created |  -  |
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** admin |  -  |
**404** | Returned if the storage does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view file links |  -  |

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
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.file_link_collection_read_model import FileLinkCollectionReadModel
from auto_slopp.openproject.openapi_client.models.file_link_collection_write_model import FileLinkCollectionWriteModel
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
    api_instance = auto_slopp.openproject.openapi_client.FileLinksApi(api_client)
    id = 1337 # int | Work package id
    file_link_collection_write_model = {"_type":"Collection","_embedded":{"elements":[{"originData":{"id":5503,"name":"logo.png","mimeType":"image/png","size":433765,"createdAt":"2021-12-19T09:42:10.170Z","lastModifiedAt":"2021-12-20T14:00:13.987Z","createdByName":"Luke Skywalker","lastModifiedByName":"Anakin Skywalker"},"_links":{"storageUrl":{"href":"https://nextcloud.deathstar.rocks/"}}}]}} # FileLinkCollectionWriteModel |  (optional)

    try:
        # Creates file links.
        api_response = api_instance.create_work_package_file_link(id, file_link_collection_write_model=file_link_collection_write_model)
        print("The response of FileLinksApi->create_work_package_file_link:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FileLinksApi->create_work_package_file_link: %s\n" % e)
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

# **delete_file_link**
> delete_file_link(id)

Removes a file link.

Removes a file link on a work package.

The request contains only the file link identifier as a path parameter. No request body is needed.

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
    api_instance = auto_slopp.openproject.openapi_client.FileLinksApi(api_client)
    id = 42 # int | File link id

    try:
        # Removes a file link.
        api_instance.delete_file_link(id)
    except Exception as e:
        print("Exception when calling FileLinksApi->delete_file_link: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| File link id | 

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
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** manage file links  *Note that you will only receive this error, if you are at least allowed to see the corresponding work package.* |  -  |
**404** | Returned if the work package or the file link does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view work package, view file links |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_storage**
> delete_storage(id)

Delete a storage

Deletes a storage resource. This also deletes all related records, like the created oauth application, client, and
any file links created within this storage.

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
    api_instance = auto_slopp.openproject.openapi_client.FileLinksApi(api_client)
    id = 1337 # int | Storage id

    try:
        # Delete a storage
        api_instance.delete_storage(id)
    except Exception as e:
        print("Exception when calling FileLinksApi->delete_storage: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Storage id | 

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
**204** | No content |  -  |
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** admin |  -  |
**404** | Returned if the storage does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view file links |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **download_file_link**
> download_file_link(id)

Creates a download uri of the linked file.

Creates a uri to download the origin file linked by the given file link. This uri depends on the storage type and
is always located on the origin storage itself.

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
    api_instance = auto_slopp.openproject.openapi_client.FileLinksApi(api_client)
    id = 42 # int | File link id

    try:
        # Creates a download uri of the linked file.
        api_instance.download_file_link(id)
    except Exception as e:
        print("Exception when calling FileLinksApi->download_file_link: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| File link id | 

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
**303** | Returned if the request was successful. In the &#x60;Location&#x60; header is the uri where the client can download the origin file from the storage. |  * Location -  <br>  |
**404** | Returned if the work package does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view work package, view file links |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_storage**
> StorageReadModel get_storage(id)

Get a storage

Gets a storage resource. As a side effect, a live connection to the storages origin is established to retrieve
connection state data.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.storage_read_model import StorageReadModel
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
    api_instance = auto_slopp.openproject.openapi_client.FileLinksApi(api_client)
    id = 1337 # int | Storage id

    try:
        # Get a storage
        api_response = api_instance.get_storage(id)
        print("The response of FileLinksApi->get_storage:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FileLinksApi->get_storage: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Storage id | 

### Return type

[**StorageReadModel**](StorageReadModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**404** | Returned if the storage does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view file links |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_storage_files**
> StorageFilesModel get_storage_files(id, parent=parent)

Gets files of a storage.

Gets a collection of files from a storage.

If no `parent` context is given, the result is the content of the document root. With `parent` context given, the
result contains the collections of files/directories from within the given parent file id.

If given `parent` context is no directory, `400 Bad Request` is returned.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.storage_files_model import StorageFilesModel
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
    api_instance = auto_slopp.openproject.openapi_client.FileLinksApi(api_client)
    id = 1337 # int | Storage id
    parent = '/my/data' # str | Parent file identification (optional)

    try:
        # Gets files of a storage.
        api_response = api_instance.get_storage_files(id, parent=parent)
        print("The response of FileLinksApi->get_storage_files:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FileLinksApi->get_storage_files: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Storage id | 
 **parent** | **str**| Parent file identification | [optional] 

### Return type

[**StorageFilesModel**](StorageFilesModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**400** | Returned if the given parent parameter value does not refer to a directory. |  -  |
**404** | Returned in either of those cases: - if the storage does not exist or the client does not have sufficient permissions to see it    **Required permission:** view file links - if the document root file identification does not exist on the storage |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_storages**
> StorageCollectionModel list_storages()

Get Storages

Returns a collection of storages.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.storage_collection_model import StorageCollectionModel
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
    api_instance = auto_slopp.openproject.openapi_client.FileLinksApi(api_client)

    try:
        # Get Storages
        api_response = api_instance.list_storages()
        print("The response of FileLinksApi->list_storages:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FileLinksApi->list_storages: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**StorageCollectionModel**](StorageCollectionModel.md)

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

# **list_work_package_file_links**
> FileLinkCollectionReadModel list_work_package_file_links(id, filters=filters)

Gets all file links of a work package

Gets all file links of a work package.

As a side effect, for every file link a request is sent to the storage's origin to fetch live data and patch
the file link's data before returning, as well as retrieving permissions of the user on this origin file. 

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.file_link_collection_read_model import FileLinkCollectionReadModel
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
    api_instance = auto_slopp.openproject.openapi_client.FileLinksApi(api_client)
    id = 1337 # int | Work package id
    filters = '[{\"storage\":{\"operator\":\"=\",\"values\":[\"42\"]}}]' # str | JSON specifying filter conditions. Accepts the same format as returned by the [queries](https://www.openproject.org/docs/api/endpoints/queries/) endpoint. The following filters are supported:  - storage (optional)

    try:
        # Gets all file links of a work package
        api_response = api_instance.list_work_package_file_links(id, filters=filters)
        print("The response of FileLinksApi->list_work_package_file_links:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FileLinksApi->list_work_package_file_links: %s\n" % e)
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

# **open_file_link**
> open_file_link(id, location=location)

Creates an opening uri of the linked file.

Creates a uri to open the origin file linked by the given file link. This uri depends on the storage type and
is always located on the origin storage itself.

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
    api_instance = auto_slopp.openproject.openapi_client.FileLinksApi(api_client)
    id = 42 # int | File link id
    location = true # bool | Boolean flag indicating, if the file should be opened directly or rather the directory location. (optional)

    try:
        # Creates an opening uri of the linked file.
        api_instance.open_file_link(id, location=location)
    except Exception as e:
        print("Exception when calling FileLinksApi->open_file_link: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| File link id | 
 **location** | **bool**| Boolean flag indicating, if the file should be opened directly or rather the directory location. | [optional] 

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
**303** | Returned if the request was successful. In the &#x60;Location&#x60; header is the uri where the client can open the origin file on the storage. |  * Location -  <br>  |
**404** | Returned if the work package does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view work package, view file links |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **prepare_storage_file_upload**
> StorageFileUploadLinkModel prepare_storage_file_upload(id, storage_file_upload_preparation_model=storage_file_upload_preparation_model)

Preparation of a direct upload of a file to the given storage.

Executes a request that prepares a link for a direct upload to the storage.

The background here is, that the client needs to make a direct request to the storage instance for file uploading,
but should not get access to the credentials, which are stored in the backend. The response contains a link object,
that enables the client to execute a file upload without the real credentials.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.storage_file_upload_link_model import StorageFileUploadLinkModel
from auto_slopp.openproject.openapi_client.models.storage_file_upload_preparation_model import StorageFileUploadPreparationModel
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
    api_instance = auto_slopp.openproject.openapi_client.FileLinksApi(api_client)
    id = 1337 # int | Storage id
    storage_file_upload_preparation_model = auto_slopp.openproject.openapi_client.StorageFileUploadPreparationModel() # StorageFileUploadPreparationModel |  (optional)

    try:
        # Preparation of a direct upload of a file to the given storage.
        api_response = api_instance.prepare_storage_file_upload(id, storage_file_upload_preparation_model=storage_file_upload_preparation_model)
        print("The response of FileLinksApi->prepare_storage_file_upload:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FileLinksApi->prepare_storage_file_upload: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Storage id | 
 **storage_file_upload_preparation_model** | [**StorageFileUploadPreparationModel**](StorageFileUploadPreparationModel.md)|  | [optional] 

### Return type

[**StorageFileUploadLinkModel**](StorageFileUploadLinkModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | OK |  -  |
**400** | Returned if the given parent parameter value does not refer to a directory. |  -  |
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** manage file links |  -  |
**404** | Returned if the storage does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view file links |  -  |
**500** | Returned if the outbound request to the storage has failed with any reason. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_storage**
> StorageReadModel update_storage(id, storage_write_model=storage_write_model)

Update a storage

Updates a storage resource. Only data that is not generated by the server can be updated. This excludes the OAuth 2
application data.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.storage_read_model import StorageReadModel
from auto_slopp.openproject.openapi_client.models.storage_write_model import StorageWriteModel
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
    api_instance = auto_slopp.openproject.openapi_client.FileLinksApi(api_client)
    id = 1337 # int | Storage id
    storage_write_model = auto_slopp.openproject.openapi_client.StorageWriteModel() # StorageWriteModel |  (optional)

    try:
        # Update a storage
        api_response = api_instance.update_storage(id, storage_write_model=storage_write_model)
        print("The response of FileLinksApi->update_storage:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FileLinksApi->update_storage: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Storage id | 
 **storage_write_model** | [**StorageWriteModel**](StorageWriteModel.md)|  | [optional] 

### Return type

[**StorageReadModel**](StorageReadModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** admin |  -  |
**404** | Returned if the storage does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view file links |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **view_file_link**
> FileLinkReadModel view_file_link(id)

Gets a file link.

Gets a single file link resource of a work package.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.file_link_read_model import FileLinkReadModel
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
    api_instance = auto_slopp.openproject.openapi_client.FileLinksApi(api_client)
    id = 42 # int | File link id

    try:
        # Gets a file link.
        api_response = api_instance.view_file_link(id)
        print("The response of FileLinksApi->view_file_link:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FileLinksApi->view_file_link: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| File link id | 

### Return type

[**FileLinkReadModel**](FileLinkReadModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**404** | Returned if the work package does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view work package, view file links |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

