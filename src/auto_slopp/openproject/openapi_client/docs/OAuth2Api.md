# auto_slopp.openproject.openapi_client.OAuth2Api

All URIs are relative to *https://openproject.melvin.beer*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_oauth_application**](OAuth2Api.md#get_oauth_application) | **GET** /api/v3/oauth_applications/{id} | Get the oauth application.
[**get_oauth_client_credentials**](OAuth2Api.md#get_oauth_client_credentials) | **GET** /api/v3/oauth_client_credentials/{id} | Get the oauth client credentials object.


# **get_oauth_application**
> OAuthApplicationReadModel get_oauth_application(id)

Get the oauth application.

Retrieves the OAuth 2 provider application for the given identifier. The secret will not be part of the response,
instead a `confidential` flag is indicating, whether there is a secret or not.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.o_auth_application_read_model import OAuthApplicationReadModel
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
    api_instance = auto_slopp.openproject.openapi_client.OAuth2Api(api_client)
    id = 1337 # int | OAuth application id

    try:
        # Get the oauth application.
        api_response = api_instance.get_oauth_application(id)
        print("The response of OAuth2Api->get_oauth_application:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OAuth2Api->get_oauth_application: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| OAuth application id | 

### Return type

[**OAuthApplicationReadModel**](OAuthApplicationReadModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** admin |  -  |
**404** | Returned if the application does not exist. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_oauth_client_credentials**
> OAuthClientCredentialsReadModel get_oauth_client_credentials(id)

Get the oauth client credentials object.

Retrieves the OAuth 2 client credentials for the given identifier. The secret will not be part of the response,
instead a `confidential` flag is indicating, whether there is a secret or not.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.o_auth_client_credentials_read_model import OAuthClientCredentialsReadModel
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
    api_instance = auto_slopp.openproject.openapi_client.OAuth2Api(api_client)
    id = 1337 # int | OAuth Client Credentials id

    try:
        # Get the oauth client credentials object.
        api_response = api_instance.get_oauth_client_credentials(id)
        print("The response of OAuth2Api->get_oauth_client_credentials:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OAuth2Api->get_oauth_client_credentials: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| OAuth Client Credentials id | 

### Return type

[**OAuthClientCredentialsReadModel**](OAuthClientCredentialsReadModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** admin |  -  |
**404** | Returned if the object does not exist. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

