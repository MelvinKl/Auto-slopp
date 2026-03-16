# ProgramModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | [optional] 
**id** | **int** | Programs&#39; id | [optional] 
**identifier** | **str** |  | [optional] 
**name** | **str** |  | [optional] 
**active** | **bool** | Indicates whether the program is currently active or already archived | [optional] 
**favorited** | **bool** | Indicates whether the program is favorited by the current user | [optional] 
**status_explanation** | [**Formattable**](Formattable.md) | A text detailing and explaining why the program has the reported status | [optional] 
**public** | **bool** | Indicates whether the program is accessible for everybody | [optional] 
**description** | [**Formattable**](Formattable.md) |  | [optional] 
**created_at** | **datetime** | Time of creation. Can be writable by admins with the &#x60;apiv3_write_readonly_attributes&#x60; setting enabled. | [optional] 
**updated_at** | **datetime** | Time of the most recent change to the program | [optional] 
**links** | [**ProgramModelAllOfLinks**](ProgramModelAllOfLinks.md) |  | [optional] 

## Example

```python
from openproject_client.models.program_model import ProgramModel

# TODO update the JSON string below
json = "{}"
# create an instance of ProgramModel from a JSON string
program_model_instance = ProgramModel.from_json(json)
# print the JSON string representation of the object
print(ProgramModel.to_json())

# convert the object into a dict
program_model_dict = program_model_instance.to_dict()
# create an instance of ProgramModel from a dict
program_model_from_dict = ProgramModel.from_dict(program_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


