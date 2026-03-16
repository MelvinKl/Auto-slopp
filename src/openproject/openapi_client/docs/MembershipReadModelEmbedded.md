# MembershipReadModelEmbedded


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**project** | [**MembershipReadModelEmbeddedProject**](MembershipReadModelEmbeddedProject.md) |  | [optional] 
**principal** | [**MembershipReadModelEmbeddedPrincipal**](MembershipReadModelEmbeddedPrincipal.md) |  | [optional] 
**roles** | [**List[RoleModel]**](RoleModel.md) |  | [optional] 

## Example

```python
from openproject_client.models.membership_read_model_embedded import MembershipReadModelEmbedded

# TODO update the JSON string below
json = "{}"
# create an instance of MembershipReadModelEmbedded from a JSON string
membership_read_model_embedded_instance = MembershipReadModelEmbedded.from_json(json)
# print the JSON string representation of the object
print(MembershipReadModelEmbedded.to_json())

# convert the object into a dict
membership_read_model_embedded_dict = membership_read_model_embedded_instance.to_dict()
# create an instance of MembershipReadModelEmbedded from a dict
membership_read_model_embedded_from_dict = MembershipReadModelEmbedded.from_dict(membership_read_model_embedded_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


