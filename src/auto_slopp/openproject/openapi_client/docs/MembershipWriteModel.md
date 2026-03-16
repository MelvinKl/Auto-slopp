# MembershipWriteModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**links** | [**MembershipWriteModelLinks**](MembershipWriteModelLinks.md) |  | 
**meta** | [**MembershipWriteModelMeta**](MembershipWriteModelMeta.md) |  | [optional] 

## Example

```python
from auto_slopp.openproject.openapi_client.models.membership_write_model import MembershipWriteModel

# TODO update the JSON string below
json = "{}"
# create an instance of MembershipWriteModel from a JSON string
membership_write_model_instance = MembershipWriteModel.from_json(json)
# print the JSON string representation of the object
print(MembershipWriteModel.to_json())

# convert the object into a dict
membership_write_model_dict = membership_write_model_instance.to_dict()
# create an instance of MembershipWriteModel from a dict
membership_write_model_from_dict = MembershipWriteModel.from_dict(membership_write_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


