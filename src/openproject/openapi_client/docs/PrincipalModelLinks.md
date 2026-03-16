# PrincipalModelLinks


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_self** | [**Link**](Link.md) | This principal resource.  **Resource**: User|Group|PlaceholderUser | 
**memberships** | [**Link**](Link.md) | An href to the collection of the principal&#39;s memberships.  # Conditions:  - user has permission &#x60;view_members&#x60; or &#x60;manage_members&#x60; in any project  **Resource**: Collection | [optional] 

## Example

```python
from openproject_client.models.principal_model_links import PrincipalModelLinks

# TODO update the JSON string below
json = "{}"
# create an instance of PrincipalModelLinks from a JSON string
principal_model_links_instance = PrincipalModelLinks.from_json(json)
# print the JSON string representation of the object
print(PrincipalModelLinks.to_json())

# convert the object into a dict
principal_model_links_dict = principal_model_links_instance.to_dict()
# create an instance of PrincipalModelLinks from a dict
principal_model_links_from_dict = PrincipalModelLinks.from_dict(principal_model_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


