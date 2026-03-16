# HelpTextModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**id** | **int** |  | 
**attribute** | **str** | The attribute the help text is assigned to. | 
**scope** | **str** |  | 
**help_text** | [**Formattable**](Formattable.md) |  | 
**links** | [**HelpTextModelLinks**](HelpTextModelLinks.md) |  | 

## Example

```python
from auto_slopp.openproject.openapi_client.models.help_text_model import HelpTextModel

# TODO update the JSON string below
json = "{}"
# create an instance of HelpTextModel from a JSON string
help_text_model_instance = HelpTextModel.from_json(json)
# print the JSON string representation of the object
print(HelpTextModel.to_json())

# convert the object into a dict
help_text_model_dict = help_text_model_instance.to_dict()
# create an instance of HelpTextModel from a dict
help_text_model_from_dict = HelpTextModel.from_dict(help_text_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


