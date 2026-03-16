# RootModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**instance_name** | **str** | The name of the OpenProject instance | 
**core_version** | **str** | The OpenProject core version number for the instance  # Conditions  **Permission** requires admin privileges | [optional] 
**links** | [**RootModelLinks**](RootModelLinks.md) |  | 

## Example

```python
from auto_slopp.openproject.openapi_client.models.root_model import RootModel

# TODO update the JSON string below
json = "{}"
# create an instance of RootModel from a JSON string
root_model_instance = RootModel.from_json(json)
# print the JSON string representation of the object
print(RootModel.to_json())

# convert the object into a dict
root_model_dict = root_model_instance.to_dict()
# create an instance of RootModel from a dict
root_model_from_dict = RootModel.from_dict(root_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


