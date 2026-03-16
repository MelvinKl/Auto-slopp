# MembershipSchemaModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**dependencies** | **List[str]** | A list of dependencies between one property&#39;s value and another property | [optional] 
**links** | [**SchemaModelLinks**](SchemaModelLinks.md) |  | 
**id** | [**SchemaPropertyModel**](SchemaPropertyModel.md) |  | 
**created_at** | [**SchemaPropertyModel**](SchemaPropertyModel.md) |  | 
**updated_at** | [**SchemaPropertyModel**](SchemaPropertyModel.md) |  | 
**notification_message** | [**SchemaPropertyModel**](SchemaPropertyModel.md) |  | 
**project** | [**SchemaPropertyModel**](SchemaPropertyModel.md) |  | 
**principal** | [**SchemaPropertyModel**](SchemaPropertyModel.md) |  | 
**roles** | [**SchemaPropertyModel**](SchemaPropertyModel.md) |  | 

## Example

```python
from openproject_client.models.membership_schema_model import MembershipSchemaModel

# TODO update the JSON string below
json = "{}"
# create an instance of MembershipSchemaModel from a JSON string
membership_schema_model_instance = MembershipSchemaModel.from_json(json)
# print the JSON string representation of the object
print(MembershipSchemaModel.to_json())

# convert the object into a dict
membership_schema_model_dict = membership_schema_model_instance.to_dict()
# create an instance of MembershipSchemaModel from a dict
membership_schema_model_from_dict = MembershipSchemaModel.from_dict(membership_schema_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


