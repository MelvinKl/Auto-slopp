# MembershipReadModelLinks


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_self** | [**Link**](Link.md) | This membership.  **Resource**: Membership | 
**var_schema** | [**Link**](Link.md) | This membership schema.  **Resource**: Schema | 
**update** | [**Link**](Link.md) | The endpoint for updating the membership.  # Conditions  **Permission**: manage_members | [optional] 
**update_immediately** | [**Link**](Link.md) | The endpoint for updating the membership without form validation.  # Conditions  **Permission**: manage_members | [optional] 
**project** | [**Link**](Link.md) | The workspace the membership is related to.  **Resource**: Workspace | 
**principal** | [**Link**](Link.md) | The principal the membership is related to.  **Resource**: Principal | 
**roles** | [**List[Link]**](Link.md) |  | 

## Example

```python
from openproject_client.models.membership_read_model_links import MembershipReadModelLinks

# TODO update the JSON string below
json = "{}"
# create an instance of MembershipReadModelLinks from a JSON string
membership_read_model_links_instance = MembershipReadModelLinks.from_json(json)
# print the JSON string representation of the object
print(MembershipReadModelLinks.to_json())

# convert the object into a dict
membership_read_model_links_dict = membership_read_model_links_instance.to_dict()
# create an instance of MembershipReadModelLinks from a dict
membership_read_model_links_from_dict = MembershipReadModelLinks.from_dict(membership_read_model_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


