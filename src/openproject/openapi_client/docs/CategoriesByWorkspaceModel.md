# CategoriesByWorkspaceModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**total** | **int** | The total amount of elements available in the collection. | 
**count** | **int** | Actual amount of elements in this response. | 
**links** | [**CategoriesByWorkspaceModelAllOfLinks**](CategoriesByWorkspaceModelAllOfLinks.md) |  | 
**embedded** | [**CategoriesByWorkspaceModelAllOfEmbedded**](CategoriesByWorkspaceModelAllOfEmbedded.md) |  | 

## Example

```python
from openproject_client.models.categories_by_workspace_model import CategoriesByWorkspaceModel

# TODO update the JSON string below
json = "{}"
# create an instance of CategoriesByWorkspaceModel from a JSON string
categories_by_workspace_model_instance = CategoriesByWorkspaceModel.from_json(json)
# print the JSON string representation of the object
print(CategoriesByWorkspaceModel.to_json())

# convert the object into a dict
categories_by_workspace_model_dict = categories_by_workspace_model_instance.to_dict()
# create an instance of CategoriesByWorkspaceModel from a dict
categories_by_workspace_model_from_dict = CategoriesByWorkspaceModel.from_dict(categories_by_workspace_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


