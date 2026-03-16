# CustomActionModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | [optional] 
**name** | **str** | The name of the custom action | [optional] 
**description** | **str** | The description for the custom action | [optional] 
**links** | [**CustomActionModelLinks**](CustomActionModelLinks.md) |  | [optional] 

## Example

```python
from auto_slopp.openproject.openapi_client.models.custom_action_model import CustomActionModel

# TODO update the JSON string below
json = "{}"
# create an instance of CustomActionModel from a JSON string
custom_action_model_instance = CustomActionModel.from_json(json)
# print the JSON string representation of the object
print(CustomActionModel.to_json())

# convert the object into a dict
custom_action_model_dict = custom_action_model_instance.to_dict()
# create an instance of CustomActionModel from a dict
custom_action_model_from_dict = CustomActionModel.from_dict(custom_action_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


