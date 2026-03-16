# ReminderModelLinks


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_self** | [**Link**](Link.md) | This reminder  **Resource**: Reminder | [optional] 
**creator** | [**Link**](Link.md) | The person that created the reminder  **Resource**: User | 
**remindable** | [**Link**](Link.md) | The resource that the reminder is associated with  **Resource**: WorkPackage | 

## Example

```python
from openproject_client.models.reminder_model_links import ReminderModelLinks

# TODO update the JSON string below
json = "{}"
# create an instance of ReminderModelLinks from a JSON string
reminder_model_links_instance = ReminderModelLinks.from_json(json)
# print the JSON string representation of the object
print(ReminderModelLinks.to_json())

# convert the object into a dict
reminder_model_links_dict = reminder_model_links_instance.to_dict()
# create an instance of ReminderModelLinks from a dict
reminder_model_links_from_dict = ReminderModelLinks.from_dict(reminder_model_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


