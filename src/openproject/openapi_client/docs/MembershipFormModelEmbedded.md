# MembershipFormModelEmbedded


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**payload** | [**MembershipWriteModel**](MembershipWriteModel.md) |  | 
**var_schema** | [**MembershipSchemaModel**](MembershipSchemaModel.md) |  | 
**validation_error** | [**MembershipFormModelEmbeddedValidationError**](MembershipFormModelEmbeddedValidationError.md) |  | 

## Example

```python
from openproject_client.models.membership_form_model_embedded import MembershipFormModelEmbedded

# TODO update the JSON string below
json = "{}"
# create an instance of MembershipFormModelEmbedded from a JSON string
membership_form_model_embedded_instance = MembershipFormModelEmbedded.from_json(json)
# print the JSON string representation of the object
print(MembershipFormModelEmbedded.to_json())

# convert the object into a dict
membership_form_model_embedded_dict = membership_form_model_embedded_instance.to_dict()
# create an instance of MembershipFormModelEmbedded from a dict
membership_form_model_embedded_from_dict = MembershipFormModelEmbedded.from_dict(membership_form_model_embedded_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


