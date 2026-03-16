# TypesByWorkspaceModelAllOfEmbeddedElements

Collection of Types

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** | Type id | [readonly] 
**name** | **str** | Type name | [readonly] 
**color** | **str** | The color used to represent this type | [readonly] 
**position** | **int** | Sort index of the type | [readonly] 
**is_default** | **bool** | Is this type active by default in new projects? | [readonly] 
**is_milestone** | **bool** | Do work packages of this type represent a milestone? | [readonly] 
**created_at** | **datetime** | Time of creation | [readonly] 
**updated_at** | **datetime** | Time of the most recent change to the user | 
**links** | [**TypeModelLinks**](TypeModelLinks.md) |  | [optional] 

## Example

```python
from openproject_client.models.types_by_workspace_model_all_of_embedded_elements import TypesByWorkspaceModelAllOfEmbeddedElements

# TODO update the JSON string below
json = "{}"
# create an instance of TypesByWorkspaceModelAllOfEmbeddedElements from a JSON string
types_by_workspace_model_all_of_embedded_elements_instance = TypesByWorkspaceModelAllOfEmbeddedElements.from_json(json)
# print the JSON string representation of the object
print(TypesByWorkspaceModelAllOfEmbeddedElements.to_json())

# convert the object into a dict
types_by_workspace_model_all_of_embedded_elements_dict = types_by_workspace_model_all_of_embedded_elements_instance.to_dict()
# create an instance of TypesByWorkspaceModelAllOfEmbeddedElements from a dict
types_by_workspace_model_all_of_embedded_elements_from_dict = TypesByWorkspaceModelAllOfEmbeddedElements.from_dict(types_by_workspace_model_all_of_embedded_elements_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


