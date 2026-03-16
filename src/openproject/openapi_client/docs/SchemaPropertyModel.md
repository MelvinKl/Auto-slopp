# SchemaPropertyModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** | The resource type for this property. | 
**name** | **str** | The name of the property. | 
**required** | **bool** | Indicates, if the property is required for submitting a request of this schema. | 
**has_default** | **bool** | Indicates, if the property has a default. | 
**writable** | **bool** | Indicates, if the property is writable when sending a request of this schema. | 
**options** | **object** | Additional options for the property. | [optional] 
**location** | **str** | Defines the json path where the property is located in the payload. | [optional] [default to '']
**placeholder** | **str** | A placeholder for the property to display if the property has no value. | [optional] 
**links** | **object** | Useful links for this property (e.g. an endpoint to fetch allowed values) | [optional] 

## Example

```python
from openproject_client.models.schema_property_model import SchemaPropertyModel

# TODO update the JSON string below
json = "{}"
# create an instance of SchemaPropertyModel from a JSON string
schema_property_model_instance = SchemaPropertyModel.from_json(json)
# print the JSON string representation of the object
print(SchemaPropertyModel.to_json())

# convert the object into a dict
schema_property_model_dict = schema_property_model_instance.to_dict()
# create an instance of SchemaPropertyModel from a dict
schema_property_model_from_dict = SchemaPropertyModel.from_dict(schema_property_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


