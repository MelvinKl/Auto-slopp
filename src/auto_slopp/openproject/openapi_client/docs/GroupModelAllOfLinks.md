# GroupModelAllOfLinks


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_self** | [**Link**](Link.md) | This group resource  **Resource**: Group | [optional] 
**members** | [**List[GroupModelAllOfLinksMembers]**](GroupModelAllOfLinksMembers.md) |  | [optional] 
**memberships** | [**Link**](Link.md) | An collection of all memberships of the group.  **Resource**: MembershipCollection | [optional] 
**delete** | [**Link**](Link.md) | An href to delete the group.  # Conditions:  - &#x60;admin&#x60; | [optional] 
**update_immediately** | [**Link**](Link.md) | An href to update the group.  # Conditions:  - &#x60;admin&#x60;  **Resource**: Group | [optional] 

## Example

```python
from auto_slopp.openproject.openapi_client.models.group_model_all_of_links import GroupModelAllOfLinks

# TODO update the JSON string below
json = "{}"
# create an instance of GroupModelAllOfLinks from a JSON string
group_model_all_of_links_instance = GroupModelAllOfLinks.from_json(json)
# print the JSON string representation of the object
print(GroupModelAllOfLinks.to_json())

# convert the object into a dict
group_model_all_of_links_dict = group_model_all_of_links_instance.to_dict()
# create an instance of GroupModelAllOfLinks from a dict
group_model_all_of_links_from_dict = GroupModelAllOfLinks.from_dict(group_model_all_of_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


