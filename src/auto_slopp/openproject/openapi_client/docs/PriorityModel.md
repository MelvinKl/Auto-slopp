# PriorityModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** | Priority id | [optional] [readonly] 
**name** | **str** | Priority name | [optional] [readonly] 
**position** | **int** | Sort index of the priority | [optional] [readonly] 
**is_default** | **bool** | Indicates whether this is the default value | [optional] [readonly] 
**is_active** | **bool** | Indicates whether the priority is available | [optional] 
**links** | [**PriorityModelLinks**](PriorityModelLinks.md) |  | [optional] 

## Example

```python
from auto_slopp.openproject.openapi_client.models.priority_model import PriorityModel

# TODO update the JSON string below
json = "{}"
# create an instance of PriorityModel from a JSON string
priority_model_instance = PriorityModel.from_json(json)
# print the JSON string representation of the object
print(PriorityModel.to_json())

# convert the object into a dict
priority_model_dict = priority_model_instance.to_dict()
# create an instance of PriorityModel from a dict
priority_model_from_dict = PriorityModel.from_dict(priority_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


