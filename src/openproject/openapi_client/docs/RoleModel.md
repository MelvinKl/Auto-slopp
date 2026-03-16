# RoleModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | [optional] 
**id** | **int** | Role id | [optional] [readonly] 
**name** | **str** | Role name | 
**links** | [**RoleModelLinks**](RoleModelLinks.md) |  | [optional] 

## Example

```python
from openproject_client.models.role_model import RoleModel

# TODO update the JSON string below
json = "{}"
# create an instance of RoleModel from a JSON string
role_model_instance = RoleModel.from_json(json)
# print the JSON string representation of the object
print(RoleModel.to_json())

# convert the object into a dict
role_model_dict = role_model_instance.to_dict()
# create an instance of RoleModel from a dict
role_model_from_dict = RoleModel.from_dict(role_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


