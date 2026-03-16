# GroupModelAllOfLinksMembers

A member of the group  # Conditions:  - user has permission `manage_members` in any project  **Resource**: User

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**href** | **str** | URL to the referenced resource (might be relative) | 
**title** | **str** | Representative label for the resource | [optional] 
**templated** | **bool** | If true the href contains parts that need to be replaced by the client | [optional] [default to False]
**method** | **str** | The HTTP verb to use when requesting the resource | [optional] [default to 'GET']
**payload** | **object** | The payload to send in the request to achieve the desired result | [optional] 
**identifier** | **str** | An optional unique identifier to the link object | [optional] 
**type** | **str** | The MIME-Type of the returned resource. | [optional] 

## Example

```python
from auto_slopp.openproject.openapi_client.models.group_model_all_of_links_members import GroupModelAllOfLinksMembers

# TODO update the JSON string below
json = "{}"
# create an instance of GroupModelAllOfLinksMembers from a JSON string
group_model_all_of_links_members_instance = GroupModelAllOfLinksMembers.from_json(json)
# print the JSON string representation of the object
print(GroupModelAllOfLinksMembers.to_json())

# convert the object into a dict
group_model_all_of_links_members_dict = group_model_all_of_links_members_instance.to_dict()
# create an instance of GroupModelAllOfLinksMembers from a dict
group_model_all_of_links_members_from_dict = GroupModelAllOfLinksMembers.from_dict(group_model_all_of_links_members_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


