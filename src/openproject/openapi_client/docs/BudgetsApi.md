# openproject_client.BudgetsApi

All URIs are relative to *https://openproject.melvin.beer*

Method | HTTP request | Description
------------- | ------------- | -------------
[**view_budget**](BudgetsApi.md#view_budget) | **GET** /api/v3/budgets/{id} | view Budget
[**view_budgets_of_a_project**](BudgetsApi.md#view_budgets_of_a_project) | **GET** /api/v3/projects/{id}/budgets | view Budgets of a Project


# **view_budget**
> BudgetModel view_budget(id)

view Budget



### Example

* Basic Authentication (BasicAuth):

```python
import openproject_client
from openproject_client.models.budget_model import BudgetModel
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
    api_instance = openproject_client.BudgetsApi(api_client)
    id = 1 # int | Budget id

    try:
        # view Budget
        api_response = api_instance.view_budget(id)
        print("The response of BudgetsApi->view_budget:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BudgetsApi->view_budget: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Budget id | 

### Return type

[**BudgetModel**](BudgetModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** view work packages **or** view budgets (on the budgets project) |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **view_budgets_of_a_project**
> object view_budgets_of_a_project(id)

view Budgets of a Project



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
    api_instance = openproject_client.BudgetsApi(api_client)
    id = 1 # int | Project id

    try:
        # view Budgets of a Project
        api_response = api_instance.view_budgets_of_a_project(id)
        print("The response of BudgetsApi->view_budgets_of_a_project:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BudgetsApi->view_budgets_of_a_project: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Project id | 

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
**403** | Returned if the client does not have sufficient permissions to see the budgets of the given project.  **Required permission:** view work packages **or** view budgets  *Note that you will only receive this error, if you are at least allowed to see the corresponding project.* |  -  |
**404** | Returned if either:  * the project does not exist  * the client does not have sufficient permissions to see the project  * the costs module is not enabled on the given project  **Required permission:** view project  *Note: A client without sufficient permissions shall not be able to test for the existence of a project. That&#39;s why a 404 is returned here, even if a 403 might be more appropriate.* |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

