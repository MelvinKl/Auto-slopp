# MembershipWriteModelMeta


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**notification_message** | [**Formattable**](Formattable.md) | A customised notification message, which will overwrite the standard notification. | [optional] 
**send_notification** | **bool** | Set to false, if no notification should get sent. | [optional] [default to True]

## Example

```python
from openproject_client.models.membership_write_model_meta import MembershipWriteModelMeta

# TODO update the JSON string below
json = "{}"
# create an instance of MembershipWriteModelMeta from a JSON string
membership_write_model_meta_instance = MembershipWriteModelMeta.from_json(json)
# print the JSON string representation of the object
print(MembershipWriteModelMeta.to_json())

# convert the object into a dict
membership_write_model_meta_dict = membership_write_model_meta_instance.to_dict()
# create an instance of MembershipWriteModelMeta from a dict
membership_write_model_meta_from_dict = MembershipWriteModelMeta.from_dict(membership_write_model_meta_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


