# MembershipFormModelLinks


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_self** | [**Link**](Link.md) | This form request.  **Resource**: Form | 
**validate** | [**List[Link]**](Link.md) |  | 
**commit** | [**Link**](Link.md) | The endpoint to create the membership with the same payload, as sent to the form.  **Resource**: Membership | 

## Example

```python
from auto_slopp.openproject.openapi_client.models.membership_form_model_links import MembershipFormModelLinks

# TODO update the JSON string below
json = "{}"
# create an instance of MembershipFormModelLinks from a JSON string
membership_form_model_links_instance = MembershipFormModelLinks.from_json(json)
# print the JSON string representation of the object
print(MembershipFormModelLinks.to_json())

# convert the object into a dict
membership_form_model_links_dict = membership_form_model_links_instance.to_dict()
# create an instance of MembershipFormModelLinks from a dict
membership_form_model_links_from_dict = MembershipFormModelLinks.from_dict(membership_form_model_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


