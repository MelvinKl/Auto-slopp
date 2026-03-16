# UserModelAllOfLinks


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**show_user** | [**Link**](Link.md) | A relative path to show the user in the web application.  # Condition  - User is not a new record - User is not &#x60;locked&#x60; | [optional] 
**update_immediately** | [**Link**](Link.md) | A link to update the user resource.  # Conditions  - &#x60;admin&#x60; | [optional] 
**lock** | [**Link**](Link.md) | Restrict the user from logging in and performing any actions.  # Conditions  - User is not locked - &#x60;admin&#x60; | [optional] 
**unlock** | [**Link**](Link.md) | Allow a locked user to login and act again.  # Conditions  - User is not locked - &#x60;admin&#x60; | [optional] 
**delete** | [**Link**](Link.md) | Permanently remove a user from the instance  # Conditions  either:   - &#x60;admin&#x60;   - Setting &#x60;users_deletable_by_admin&#x60; is set or:   - User is self   - Setting &#x60;users_deletable_by_self&#x60; is set | [optional] 
**auth_source** | [**Link**](Link.md) | Permanently remove a user from the instance  # Conditions  - LDAP authentication configured - &#x60;admin&#x60; | [optional] 

## Example

```python
from auto_slopp.openproject.openapi_client.models.user_model_all_of_links import UserModelAllOfLinks

# TODO update the JSON string below
json = "{}"
# create an instance of UserModelAllOfLinks from a JSON string
user_model_all_of_links_instance = UserModelAllOfLinks.from_json(json)
# print the JSON string representation of the object
print(UserModelAllOfLinks.to_json())

# convert the object into a dict
user_model_all_of_links_dict = user_model_all_of_links_instance.to_dict()
# create an instance of UserModelAllOfLinks from a dict
user_model_all_of_links_from_dict = UserModelAllOfLinks.from_dict(user_model_all_of_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


