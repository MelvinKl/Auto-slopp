# GroupWriteModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | The new group name. | [optional] 
**links** | [**GroupWriteModelLinks**](GroupWriteModelLinks.md) |  | [optional] 

## Example

```python
from openproject_client.models.group_write_model import GroupWriteModel

# TODO update the JSON string below
json = "{}"
# create an instance of GroupWriteModel from a JSON string
group_write_model_instance = GroupWriteModel.from_json(json)
# print the JSON string representation of the object
print(GroupWriteModel.to_json())

# convert the object into a dict
group_write_model_dict = group_write_model_instance.to_dict()
# create an instance of GroupWriteModel from a dict
group_write_model_from_dict = GroupWriteModel.from_dict(group_write_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


