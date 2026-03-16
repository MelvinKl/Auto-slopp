# CustomOptionModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** | The identifier | [optional] [readonly] 
**value** | **str** | The value defined for this custom option | [optional] [readonly] 
**links** | [**CustomOptionModelLinks**](CustomOptionModelLinks.md) |  | [optional] 

## Example

```python
from auto_slopp.openproject.openapi_client.models.custom_option_model import CustomOptionModel

# TODO update the JSON string below
json = "{}"
# create an instance of CustomOptionModel from a JSON string
custom_option_model_instance = CustomOptionModel.from_json(json)
# print the JSON string representation of the object
print(CustomOptionModel.to_json())

# convert the object into a dict
custom_option_model_dict = custom_option_model_instance.to_dict()
# create an instance of CustomOptionModel from a dict
custom_option_model_from_dict = CustomOptionModel.from_dict(custom_option_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


