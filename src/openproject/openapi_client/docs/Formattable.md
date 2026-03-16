# Formattable


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**format** | **str** | Indicates the formatting language of the raw text | [readonly] 
**raw** | **str** | The raw text, as entered by the user | [optional] 
**html** | **str** | The text converted to HTML according to the format | [optional] [readonly] 

## Example

```python
from openproject_client.models.formattable import Formattable

# TODO update the JSON string below
json = "{}"
# create an instance of Formattable from a JSON string
formattable_instance = Formattable.from_json(json)
# print the JSON string representation of the object
print(Formattable.to_json())

# convert the object into a dict
formattable_dict = formattable_instance.to_dict()
# create an instance of Formattable from a dict
formattable_from_dict = Formattable.from_dict(formattable_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


