# MembershipFormModelEmbeddedValidationError


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**base** | [**ErrorResponse**](ErrorResponse.md) |  | [optional] 
**principal** | [**ErrorResponse**](ErrorResponse.md) |  | [optional] 
**roles** | [**ErrorResponse**](ErrorResponse.md) |  | [optional] 

## Example

```python
from auto_slopp.openproject.openapi_client.models.membership_form_model_embedded_validation_error import MembershipFormModelEmbeddedValidationError

# TODO update the JSON string below
json = "{}"
# create an instance of MembershipFormModelEmbeddedValidationError from a JSON string
membership_form_model_embedded_validation_error_instance = MembershipFormModelEmbeddedValidationError.from_json(json)
# print the JSON string representation of the object
print(MembershipFormModelEmbeddedValidationError.to_json())

# convert the object into a dict
membership_form_model_embedded_validation_error_dict = membership_form_model_embedded_validation_error_instance.to_dict()
# create an instance of MembershipFormModelEmbeddedValidationError from a dict
membership_form_model_embedded_validation_error_from_dict = MembershipFormModelEmbeddedValidationError.from_dict(membership_form_model_embedded_validation_error_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


