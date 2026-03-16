# MembershipFormModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**embedded** | [**MembershipFormModelEmbedded**](MembershipFormModelEmbedded.md) |  | 
**links** | [**MembershipFormModelLinks**](MembershipFormModelLinks.md) |  | 

## Example

```python
from auto_slopp.openproject.openapi_client.models.membership_form_model import MembershipFormModel

# TODO update the JSON string below
json = "{}"
# create an instance of MembershipFormModel from a JSON string
membership_form_model_instance = MembershipFormModel.from_json(json)
# print the JSON string representation of the object
print(MembershipFormModel.to_json())

# convert the object into a dict
membership_form_model_dict = membership_form_model_instance.to_dict()
# create an instance of MembershipFormModel from a dict
membership_form_model_from_dict = MembershipFormModel.from_dict(membership_form_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


