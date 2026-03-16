# SchemaModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**dependencies** | **List[str]** | A list of dependencies between one property&#39;s value and another property | [optional] 
**links** | [**SchemaModelLinks**](SchemaModelLinks.md) |  | 

## Example

```python
from auto_slopp.openproject.openapi_client.models.schema_model import SchemaModel

# TODO update the JSON string below
json = "{}"
# create an instance of SchemaModel from a JSON string
schema_model_instance = SchemaModel.from_json(json)
# print the JSON string representation of the object
print(SchemaModel.to_json())

# convert the object into a dict
schema_model_dict = schema_model_instance.to_dict()
# create an instance of SchemaModel from a dict
schema_model_from_dict = SchemaModel.from_dict(schema_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


