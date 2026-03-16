# TypeModel


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
from openproject_client.models.type_model import TypeModel

# TODO update the JSON string below
json = "{}"
# create an instance of TypeModel from a JSON string
type_model_instance = TypeModel.from_json(json)
# print the JSON string representation of the object
print(TypeModel.to_json())

# convert the object into a dict
type_model_dict = type_model_instance.to_dict()
# create an instance of TypeModel from a dict
type_model_from_dict = TypeModel.from_dict(type_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


