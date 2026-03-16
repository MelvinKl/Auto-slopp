# openproject_client.QueryOperatorsApi

All URIs are relative to *https://openproject.melvin.beer*

Method | HTTP request | Description
------------- | ------------- | -------------
[**view_query_operator**](QueryOperatorsApi.md#view_query_operator) | **GET** /api/v3/queries/operators/{id} | View Query Operator


# **view_query_operator**
> QueryOperatorModel view_query_operator(id)

View Query Operator

Retrieve an individual QueryOperator as identified by the `id` parameter.

### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.query_operator_model import QueryOperatorModel
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
    api_instance = openproject_client.QueryOperatorsApi(api_client)
    id = '!' # str | QueryOperator id

    try:
        # View Query Operator
        api_response = api_instance.view_query_operator(id)
        print("The response of QueryOperatorsApi->view_query_operator:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling QueryOperatorsApi->view_query_operator: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| QueryOperator id | 

### Return type

[**QueryOperatorModel**](QueryOperatorModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**403** | Returned if the client does not have sufficient permissions to see it.  **Required permission:** view work package in any project |  -  |
**404** | Returned if the QueryOperator does not exist. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

