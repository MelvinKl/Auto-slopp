# PortfolioModelAllOfLinks


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**update** | [**Link**](Link.md) | Form endpoint that aids in updating this portfolio  # Conditions  **Permission**: edit workspace | [optional] 
**update_immediately** | [**Link**](Link.md) | Directly update this portfolio  # Conditions  **Permission**: edit workspace | [optional] 
**delete** | [**Link**](Link.md) | Delete this portfolio  # Conditions  **Permission**: admin | [optional] 
**favor** | [**Link**](Link.md) | Mark this portfolio as favorited by the current user  # Conditions  Only present if the portfolio is not yet favorited  Permission**: none but login is required | [optional] 
**disfavor** | [**Link**](Link.md) | Mark this portfolio as not favorited by the current user  # Conditions Only present if the portfolio is favorited by the current user  Permission**: none but login is required | [optional] 
**create_work_package** | [**Link**](Link.md) | Form endpoint that aids in preparing and creating a work package  # Conditions  **Permission**: add work packages | [optional] 
**create_work_package_immediately** | [**Link**](Link.md) | Directly creates a work package in the portfolio  # Conditions  **Permission**: add work packages | [optional] 
**var_self** | [**Link**](Link.md) | This portfolio  **Resource**: Portfolio | 
**categories** | [**Link**](Link.md) | Categories available in this portfolio  **Resource**: Collection | 
**types** | [**Link**](Link.md) | Types available in this portfolio  **Resource**: Collection  # Conditions  **Permission**: view work packages or manage types | [optional] 
**versions** | [**Link**](Link.md) | Versions available in this portfolio  **Resource**: Collection  # Conditions  **Permission**: view work packages or manage versions | [optional] 
**memberships** | [**Link**](Link.md) | Memberships in the  portfolio  **Resource**: Collection  # Conditions  **Permission**: view members | [optional] 
**work_packages** | [**Link**](Link.md) | Work Packages of this portfolio  **Resource**: Collection | [optional] 
**parent** | [**Link**](Link.md) | Parent of the portfolio  **Resource**: Portfolio  # Conditions  **Permission** edit workspace | [optional] 
**status** | [**Link**](Link.md) | Denotes the status of the portfolio, so whether the portfolio is on track, at risk or is having trouble.  **Resource**: ProjectStatus  # Conditions  **Permission** edit workspace | [optional] 
**storages** | [**List[PortfolioModelAllOfLinksStorages]**](PortfolioModelAllOfLinksStorages.md) |  | [optional] 
**project_storages** | [**Link**](Link.md) | The project storage collection of this portfolio.  **Resource**: Collection  # Conditions  **Permission**: view_file_links | [optional] 
**ancestors** | [**List[PortfolioModelAllOfLinksAncestors]**](PortfolioModelAllOfLinksAncestors.md) |  | [optional] 

## Example

```python
from openproject_client.models.portfolio_model_all_of_links import PortfolioModelAllOfLinks

# TODO update the JSON string below
json = "{}"
# create an instance of PortfolioModelAllOfLinks from a JSON string
portfolio_model_all_of_links_instance = PortfolioModelAllOfLinks.from_json(json)
# print the JSON string representation of the object
print(PortfolioModelAllOfLinks.to_json())

# convert the object into a dict
portfolio_model_all_of_links_dict = portfolio_model_all_of_links_instance.to_dict()
# create an instance of PortfolioModelAllOfLinks from a dict
portfolio_model_all_of_links_from_dict = PortfolioModelAllOfLinks.from_dict(portfolio_model_all_of_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


