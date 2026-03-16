# ValuesPropertyModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**var_property** | **str** | The key of the key - value pair represented by the Values::Property | 
**value** | **str** | The value of the key - value pair represented by the Values::Property | 
**links** | [**ValuesPropertyModelLinks**](ValuesPropertyModelLinks.md) |  | 

## Example

```python
from auto_slopp.openproject.openapi_client.models.values_property_model import ValuesPropertyModel

# TODO update the JSON string below
json = "{}"
# create an instance of ValuesPropertyModel from a JSON string
values_property_model_instance = ValuesPropertyModel.from_json(json)
# print the JSON string representation of the object
print(ValuesPropertyModel.to_json())

# convert the object into a dict
values_property_model_dict = values_property_model_instance.to_dict()
# create an instance of ValuesPropertyModel from a dict
values_property_model_from_dict = ValuesPropertyModel.from_dict(values_property_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


