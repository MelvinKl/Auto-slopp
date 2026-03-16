# auto_slopp.openproject.openapi_client.PortfoliosApi

All URIs are relative to *https://openproject.melvin.beer*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_portfolio**](PortfoliosApi.md#delete_portfolio) | **DELETE** /api/v3/portfolios/{id} | Delete Portfolio
[**list_portfolios**](PortfoliosApi.md#list_portfolios) | **GET** /api/v3/portfolios | List portfolios
[**portfolio_update_form**](PortfoliosApi.md#portfolio_update_form) | **POST** /api/v3/portfolios/{id}/form | Portfolio update form
[**update_portfolio**](PortfoliosApi.md#update_portfolio) | **PATCH** /api/v3/portfolios/{id} | Update Portfolio
[**view_portfolio**](PortfoliosApi.md#view_portfolio) | **GET** /api/v3/portfolios/{id} | View portfolio


# **delete_portfolio**
> delete_portfolio(id)

Delete Portfolio

Deletes the portfolio permanently. As this is a lengthy process, the actual deletion is carried out asynchronously.
So the portfolio might exist well after the request has returned successfully. To prevent unwanted changes to
the portfolio scheduled for deletion, it is archived at once.

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
    api_instance = auto_slopp.openproject.openapi_client.PortfoliosApi(api_client)
    id = 1 # int | Portfolio id

    try:
        # Delete Portfolio
        api_instance.delete_portfolio(id)
    except Exception as e:
        print("Exception when calling PortfoliosApi->delete_portfolio: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Portfolio id | 

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
**204** | Returned if the portfolio was successfully deleted. There is currently no endpoint to query for the actual deletion status. Such an endpoint _might_ be added in the future. |  -  |
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** admin |  -  |
**404** | Returned if the portfolio does not exist or the client does not have sufficient permissions to see it.  **Required permission:** any permission in the portfolio  *Note: A client without sufficient permissions shall not be able to test for the existence of a version. That&#39;s why a 404 is returned here, even if a 403 might be more appropriate.* |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |
**422** | Returned if the portfolio cannot be deleted. This can happen when there are still references to the portfolio in other workspaces that need to be severed at first. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_portfolios**
> PortfolioCollectionModel list_portfolios(filters=filters, sort_by=sort_by, select=select)

List portfolios

Returns a collection of portfolios. The collection can be filtered via query parameters similar to how work packages are filtered. In addition to the provided filter, the result set is always limited to only contain portfolios the client is allowed to see.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.portfolio_collection_model import PortfolioCollectionModel
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
    api_instance = auto_slopp.openproject.openapi_client.PortfoliosApi(api_client)
    filters = '[{ \"ancestor\": { \"operator\": \"=\", \"values\": [\"1\"] }\" }]' # str | JSON specifying filter conditions. Accepts the same format as returned by the [queries](https://www.openportfolio.org/docs/api/endpoints/queries/) endpoint. Currently supported filters are:  + active: based on the active property of the portfolio + ancestor: filters portfolios by their ancestor. A portfolio is not considered to be its own ancestor. + available_project_attributes: filters portfolios based on the activated project attributes. + created_at: based on the time the portfolio was created + favorited: based on the favorited property of the portfolio + id: based on portfolios' id. + latest_activity_at: based on the time the last activity was registered on a portfolio. + name_and_identifier: based on both the name and the identifier. + parent_id: filters portfolios by their parent. + principal: based on members of the portfolio. + project_phase_any: based on the project phases active in a portfolio. + project_status_code: based on status code of the portfolio + storage_id: filters portfolios by linked storages + storage_url: filters portfolios by linked storages identified by the host url + type_id: based on the types active in a portfolio. + user_action: based on the actions the current user has in the portfolio. + visible: based on the visibility for the user (id) provided as the filter value. This filter is useful for admins to identify the portfolios visible to a user.  There might also be additional filters based on the custom fields that have been configured.  Each defined lifecycle step will also define a filter in this list endpoint. Given that the elements are not static but rather dynamically created on each OpenProject instance, a list cannot be provided. Those filters follow the schema: + project_start_gate_[id]: a filter on a project phase's start gate active in a portfolio. The id is the id of the phase the gate belongs to. + project_finish_gate_[id]: a filter on a project phase's finish gate active in a portfolio. The id is the id of the phase the gate belongs to. + project_phase_[id]: a filter on a project phase active in a portfolio. The id is the id of the phase queried for. (optional)
    sort_by = '[[\"id\", \"asc\"]]' # str | JSON specifying sort criteria. Currently supported orders are:  + id + name + typeahead (sorting by hierarchy and name) + created_at + public + latest_activity_at + required_disk_space  There might also be additional orders based on the custom fields that have been configured. (optional)
    select = 'total,elements/identifier,elements/name' # str | Comma separated list of properties to include. (optional)

    try:
        # List portfolios
        api_response = api_instance.list_portfolios(filters=filters, sort_by=sort_by, select=select)
        print("The response of PortfoliosApi->list_portfolios:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PortfoliosApi->list_portfolios: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **filters** | **str**| JSON specifying filter conditions. Accepts the same format as returned by the [queries](https://www.openportfolio.org/docs/api/endpoints/queries/) endpoint. Currently supported filters are:  + active: based on the active property of the portfolio + ancestor: filters portfolios by their ancestor. A portfolio is not considered to be its own ancestor. + available_project_attributes: filters portfolios based on the activated project attributes. + created_at: based on the time the portfolio was created + favorited: based on the favorited property of the portfolio + id: based on portfolios&#39; id. + latest_activity_at: based on the time the last activity was registered on a portfolio. + name_and_identifier: based on both the name and the identifier. + parent_id: filters portfolios by their parent. + principal: based on members of the portfolio. + project_phase_any: based on the project phases active in a portfolio. + project_status_code: based on status code of the portfolio + storage_id: filters portfolios by linked storages + storage_url: filters portfolios by linked storages identified by the host url + type_id: based on the types active in a portfolio. + user_action: based on the actions the current user has in the portfolio. + visible: based on the visibility for the user (id) provided as the filter value. This filter is useful for admins to identify the portfolios visible to a user.  There might also be additional filters based on the custom fields that have been configured.  Each defined lifecycle step will also define a filter in this list endpoint. Given that the elements are not static but rather dynamically created on each OpenProject instance, a list cannot be provided. Those filters follow the schema: + project_start_gate_[id]: a filter on a project phase&#39;s start gate active in a portfolio. The id is the id of the phase the gate belongs to. + project_finish_gate_[id]: a filter on a project phase&#39;s finish gate active in a portfolio. The id is the id of the phase the gate belongs to. + project_phase_[id]: a filter on a project phase active in a portfolio. The id is the id of the phase queried for. | [optional] 
 **sort_by** | **str**| JSON specifying sort criteria. Currently supported orders are:  + id + name + typeahead (sorting by hierarchy and name) + created_at + public + latest_activity_at + required_disk_space  There might also be additional orders based on the custom fields that have been configured. | [optional] 
 **select** | **str**| Comma separated list of properties to include. | [optional] 

### Return type

[**PortfolioCollectionModel**](PortfolioCollectionModel.md)

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

# **portfolio_update_form**
> portfolio_update_form(id, body=body)

Portfolio update form



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
    api_instance = auto_slopp.openproject.openapi_client.PortfoliosApi(api_client)
    id = 1 # int | Portfolio id
    body = None # object |  (optional)

    try:
        # Portfolio update form
        api_instance.portfolio_update_form(id, body=body)
    except Exception as e:
        print("Exception when calling PortfoliosApi->portfolio_update_form: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Portfolio id | 
 **body** | **object**|  | [optional] 

### Return type

void (empty response body)

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
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** edit workspace in the portfolio |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_portfolio**
> PortfolioModel update_portfolio(id, portfolio_model=portfolio_model)

Update Portfolio

Updates the given portfolio by applying the attributes provided in the body.

### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.portfolio_model import PortfolioModel
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
    api_instance = auto_slopp.openproject.openapi_client.PortfoliosApi(api_client)
    id = 1 # int | Portfolio id
    portfolio_model = auto_slopp.openproject.openapi_client.PortfolioModel() # PortfolioModel |  (optional)

    try:
        # Update Portfolio
        api_response = api_instance.update_portfolio(id, portfolio_model=portfolio_model)
        print("The response of PortfoliosApi->update_portfolio:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PortfoliosApi->update_portfolio: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Portfolio id | 
 **portfolio_model** | [**PortfolioModel**](PortfolioModel.md)|  | [optional] 

### Return type

[**PortfolioModel**](PortfolioModel.md)

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
**403** | Returned if the client does not have sufficient permissions.  **Required permission:** edit project for the portfolio to be altered |  -  |
**404** | Returned if the portfolio does not exist or the client does not have sufficient permissions to see it.  **Required permission:** view project  *Note: A client without sufficient permissions shall not be able to test for the existence of a version. That&#39;s why a 404 is returned here, even if a 403 might be more appropriate.* |  -  |
**406** | Occurs when the client did not send a Content-Type header |  -  |
**415** | Occurs when the client sends an unsupported Content-Type header. |  -  |
**422** | Returned if:  * a constraint for a property was violated (&#x60;PropertyConstraintViolation&#x60;) |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **view_portfolio**
> PortfolioModel view_portfolio(id)

View portfolio



### Example

* Basic Authentication (BasicAuth):

```python
import auto_slopp.openproject.openapi_client
from auto_slopp.openproject.openapi_client.models.portfolio_model import PortfolioModel
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
    api_instance = auto_slopp.openproject.openapi_client.PortfoliosApi(api_client)
    id = 1 # int | Portfolio id

    try:
        # View portfolio
        api_response = api_instance.view_portfolio(id)
        print("The response of PortfoliosApi->view_portfolio:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PortfoliosApi->view_portfolio: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Portfolio id | 

### Return type

[**PortfolioModel**](PortfolioModel.md)

### Authorization

[BasicAuth](../README.md#BasicAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**404** | Returned if the portfolio does not exist or the client does not have sufficient permissions to see it.  **Required permission:** any permission in the portfolio  *Note: A client without sufficient permissions shall not be able to test for the existence of a portfolio. That&#39;s why a 404 is returned here, even if a 403 might be more appropriate.* |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

