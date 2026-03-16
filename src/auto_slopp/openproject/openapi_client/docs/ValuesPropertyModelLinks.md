# ValuesPropertyModelLinks


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_self** | [**Link**](Link.md) | This key - value pair.  **Resource**: Storage | 
**var_schema** | [**Link**](Link.md) | The schema describing the key - value pair.  **Resource**: Schema | 

## Example

```python
from auto_slopp.openproject.openapi_client.models.values_property_model_links import ValuesPropertyModelLinks

# TODO update the JSON string below
json = "{}"
# create an instance of ValuesPropertyModelLinks from a JSON string
values_property_model_links_instance = ValuesPropertyModelLinks.from_json(json)
# print the JSON string representation of the object
print(ValuesPropertyModelLinks.to_json())

# convert the object into a dict
values_property_model_links_dict = values_property_model_links_instance.to_dict()
# create an instance of ValuesPropertyModelLinks from a dict
values_property_model_links_from_dict = ValuesPropertyModelLinks.from_dict(values_property_model_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


