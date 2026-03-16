# ListAvailableParentProjectCandidatesModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**total** | **int** | The total amount of elements available in the collection. | 
**count** | **int** | Actual amount of elements in this response. | 
**links** | [**ListAvailableParentProjectCandidatesModelAllOfLinks**](ListAvailableParentProjectCandidatesModelAllOfLinks.md) |  | 
**embedded** | [**ListAvailableParentProjectCandidatesModelAllOfEmbedded**](ListAvailableParentProjectCandidatesModelAllOfEmbedded.md) |  | 

## Example

```python
from auto_slopp.openproject.openapi_client.models.list_available_parent_project_candidates_model import ListAvailableParentProjectCandidatesModel

# TODO update the JSON string below
json = "{}"
# create an instance of ListAvailableParentProjectCandidatesModel from a JSON string
list_available_parent_project_candidates_model_instance = ListAvailableParentProjectCandidatesModel.from_json(json)
# print the JSON string representation of the object
print(ListAvailableParentProjectCandidatesModel.to_json())

# convert the object into a dict
list_available_parent_project_candidates_model_dict = list_available_parent_project_candidates_model_instance.to_dict()
# create an instance of ListAvailableParentProjectCandidatesModel from a dict
list_available_parent_project_candidates_model_from_dict = ListAvailableParentProjectCandidatesModel.from_dict(list_available_parent_project_candidates_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


