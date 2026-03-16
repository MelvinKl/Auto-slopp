# PortfolioModelAllOfLinksStorages

The link to a storage that is active for this portfolio.  **Resource**: Storage  # Conditions  **Permission**: view_file_links

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**href** | **str** | URL to the referenced resource (might be relative) | 
**title** | **str** | Representative label for the resource | [optional] 
**templated** | **bool** | If true the href contains parts that need to be replaced by the client | [optional] [default to False]
**method** | **str** | The HTTP verb to use when requesting the resource | [optional] [default to 'GET']
**payload** | **object** | The payload to send in the request to achieve the desired result | [optional] 
**identifier** | **str** | An optional unique identifier to the link object | [optional] 
**type** | **str** | The MIME-Type of the returned resource. | [optional] 

## Example

```python
from auto_slopp.openproject.openapi_client.models.portfolio_model_all_of_links_storages import PortfolioModelAllOfLinksStorages

# TODO update the JSON string below
json = "{}"
# create an instance of PortfolioModelAllOfLinksStorages from a JSON string
portfolio_model_all_of_links_storages_instance = PortfolioModelAllOfLinksStorages.from_json(json)
# print the JSON string representation of the object
print(PortfolioModelAllOfLinksStorages.to_json())

# convert the object into a dict
portfolio_model_all_of_links_storages_dict = portfolio_model_all_of_links_storages_instance.to_dict()
# create an instance of PortfolioModelAllOfLinksStorages from a dict
portfolio_model_all_of_links_storages_from_dict = PortfolioModelAllOfLinksStorages.from_dict(portfolio_model_all_of_links_storages_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


