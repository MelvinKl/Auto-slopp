# ListAvailableParentProjectCandidatesModelAllOfEmbeddedElements


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | [optional] 
**id** | **int** | Portfolios&#39; id | [optional] 
**identifier** | **str** |  | [optional] 
**name** | **str** |  | [optional] 
**active** | **bool** | Indicates whether the portfolio is currently active or already archived | [optional] 
**favorited** | **bool** | Indicates whether the portfolio is favorited by the current user | [optional] 
**status_explanation** | [**Formattable**](Formattable.md) | A text detailing and explaining why the portfolio has the reported status | [optional] 
**public** | **bool** | Indicates whether the portfolio is accessible for everybody | [optional] 
**description** | [**Formattable**](Formattable.md) |  | [optional] 
**created_at** | **datetime** | Time of creation. Can be writable by admins with the &#x60;apiv3_write_readonly_attributes&#x60; setting enabled. | [optional] 
**updated_at** | **datetime** | Time of the most recent change to the portfolio | [optional] 
**links** | [**PortfolioModelAllOfLinks**](PortfolioModelAllOfLinks.md) |  | [optional] 

## Example

```python
from auto_slopp.openproject.openapi_client.models.list_available_parent_project_candidates_model_all_of_embedded_elements import ListAvailableParentProjectCandidatesModelAllOfEmbeddedElements

# TODO update the JSON string below
json = "{}"
# create an instance of ListAvailableParentProjectCandidatesModelAllOfEmbeddedElements from a JSON string
list_available_parent_project_candidates_model_all_of_embedded_elements_instance = ListAvailableParentProjectCandidatesModelAllOfEmbeddedElements.from_json(json)
# print the JSON string representation of the object
print(ListAvailableParentProjectCandidatesModelAllOfEmbeddedElements.to_json())

# convert the object into a dict
list_available_parent_project_candidates_model_all_of_embedded_elements_dict = list_available_parent_project_candidates_model_all_of_embedded_elements_instance.to_dict()
# create an instance of ListAvailableParentProjectCandidatesModelAllOfEmbeddedElements from a dict
list_available_parent_project_candidates_model_all_of_embedded_elements_from_dict = ListAvailableParentProjectCandidatesModelAllOfEmbeddedElements.from_dict(list_available_parent_project_candidates_model_all_of_embedded_elements_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


