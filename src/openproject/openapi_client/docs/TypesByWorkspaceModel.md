# TypesByWorkspaceModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**total** | **int** | The total amount of elements available in the collection. | 
**count** | **int** | Actual amount of elements in this response. | 
**links** | [**TypesByWorkspaceModelAllOfLinks**](TypesByWorkspaceModelAllOfLinks.md) |  | 
**embedded** | [**TypesByWorkspaceModelAllOfEmbedded**](TypesByWorkspaceModelAllOfEmbedded.md) |  | 

## Example

```python
from openproject_client.models.types_by_workspace_model import TypesByWorkspaceModel

# TODO update the JSON string below
json = "{}"
# create an instance of TypesByWorkspaceModel from a JSON string
types_by_workspace_model_instance = TypesByWorkspaceModel.from_json(json)
# print the JSON string representation of the object
print(TypesByWorkspaceModel.to_json())

# convert the object into a dict
types_by_workspace_model_dict = types_by_workspace_model_instance.to_dict()
# create an instance of TypesByWorkspaceModel from a dict
types_by_workspace_model_from_dict = TypesByWorkspaceModel.from_dict(types_by_workspace_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


