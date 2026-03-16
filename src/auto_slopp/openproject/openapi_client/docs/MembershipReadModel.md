# MembershipReadModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**id** | **int** | The membership&#39;s id | 
**created_at** | **datetime** | The time the membership was created. | 
**updated_at** | **datetime** | The time the membership was last updated. | 
**embedded** | [**MembershipReadModelEmbedded**](MembershipReadModelEmbedded.md) |  | [optional] 
**links** | [**MembershipReadModelLinks**](MembershipReadModelLinks.md) |  | 

## Example

```python
from auto_slopp.openproject.openapi_client.models.membership_read_model import MembershipReadModel

# TODO update the JSON string below
json = "{}"
# create an instance of MembershipReadModel from a JSON string
membership_read_model_instance = MembershipReadModel.from_json(json)
# print the JSON string representation of the object
print(MembershipReadModel.to_json())

# convert the object into a dict
membership_read_model_dict = membership_read_model_instance.to_dict()
# create an instance of MembershipReadModel from a dict
membership_read_model_from_dict = MembershipReadModel.from_dict(membership_read_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


