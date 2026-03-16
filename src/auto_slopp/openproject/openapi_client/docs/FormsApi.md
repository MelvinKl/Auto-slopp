# auto_slopp.openproject.openapi_client.FormsApi

All URIs are relative to *https://openproject.melvin.beer*

Method | HTTP request | Description
------------- | ------------- | -------------
[**show_or_validate_form**](FormsApi.md#show_or_validate_form) | **POST** /api/v3/example/form | show or validate form


# **show_or_validate_form**
> object show_or_validate_form(show_or_validate_form_request=show_or_validate_form_request)

show or validate form

This is an example of how a form might look like. Note that this endpoint does not exist in the actual implementation.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.show_or_validate_form_request import ShowOrValidateFormRequest
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
    api_instance = auto_slopp.openproject.openapi_client.FormsApi(api_client)
    show_or_validate_form_request = auto_slopp.openproject.openapi_client.ShowOrValidateFormRequest() # ShowOrValidateFormRequest |  (optional)

    try:
        # show or validate form
        api_response = api_instance.show_or_validate_form(show_or_validate_form_request=show_or_validate_form_request)
        print("The response of FormsApi->show_or_validate_form:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FormsApi->show_or_validate_form: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **show_or_validate_form_request** | [**ShowOrValidateFormRequest**](ShowOrValidateFormRequest.md)|  | [optional] 

### Return type

**object**

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/hal+json, text/plain

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**400** | Occurs when the client did not send a valid JSON object in the request body and the request body was not empty.  Note that this error only occurs when the content is not at all a single JSON object. It **does not occur** for requests containing undefined properties or invalid property values. |  -  |
**403** | Returned if the client does not have sufficient permissions to modify the associated resource. |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**409** | Returned if underlying resource was changed since the client requested the form. This is determined using the &#x60;lockVersion&#x60; property. |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

