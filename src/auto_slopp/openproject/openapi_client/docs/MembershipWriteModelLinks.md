# MembershipWriteModelLinks


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**principal** | [**Link**](Link.md) | The principal that is to get a membership.  **Resource**: Principal | [optional] 
**roles** | [**List[Link]**](Link.md) |  | [optional] 
**project** | [**Link**](Link.md) | The project that is to get a membership. If no project is given, the principal&#39;s membership is supposed to be global.  **Resource**: Project | [optional] 

## Example

```python
from auto_slopp.openproject.openapi_client.models.membership_write_model_links import MembershipWriteModelLinks

# TODO update the JSON string below
json = "{}"
# create an instance of MembershipWriteModelLinks from a JSON string
membership_write_model_links_instance = MembershipWriteModelLinks.from_json(json)
# print the JSON string representation of the object
print(MembershipWriteModelLinks.to_json())

# convert the object into a dict
membership_write_model_links_dict = membership_write_model_links_instance.to_dict()
# create an instance of MembershipWriteModelLinks from a dict
membership_write_model_links_from_dict = MembershipWriteModelLinks.from_dict(membership_write_model_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


