# ActivityModelLinks


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_self** | [**Link**](Link.md) | This activity  **Resource**: Activity | [optional] 
**work_package** | [**Link**](Link.md) | The work package this activity belongs to  **Resource**: WorkPackage | [optional] 
**user** | [**Link**](Link.md) | The user who created this activity  **Resource**: Principal | [optional] 
**update** | [**Link**](Link.md) | Update this activity | [optional] 
**attachments** | [**Link**](Link.md) | The attachment collection of this activity  **Resource**: Attachments | [optional] 
**add_attachment** | [**Link**](Link.md) | Attach a file to the activity  # Conditions  **Permissions**: - &#x60;add_work_package_comments&#x60; - for internal comments: &#x60;add_internal_comments&#x60; | [optional] 
**emoji_reactions** | [**Link**](Link.md) | The emoji reactions collection of this activity  **Resource**: EmojiReactions | [optional] 

## Example

```python
from openproject_client.models.activity_model_links import ActivityModelLinks

# TODO update the JSON string below
json = "{}"
# create an instance of ActivityModelLinks from a JSON string
activity_model_links_instance = ActivityModelLinks.from_json(json)
# print the JSON string representation of the object
print(ActivityModelLinks.to_json())

# convert the object into a dict
activity_model_links_dict = activity_model_links_instance.to_dict()
# create an instance of ActivityModelLinks from a dict
activity_model_links_from_dict = ActivityModelLinks.from_dict(activity_model_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


