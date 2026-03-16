# UpdateReminderRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**remind_at** | **datetime** | The date and time when the reminder is due | [optional] 
**note** | **str** | The note of the reminder (optional) | [optional] 

## Example

```python
from openproject_client.models.update_reminder_request import UpdateReminderRequest

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateReminderRequest from a JSON string
update_reminder_request_instance = UpdateReminderRequest.from_json(json)
# print the JSON string representation of the object
print(UpdateReminderRequest.to_json())

# convert the object into a dict
update_reminder_request_dict = update_reminder_request_instance.to_dict()
# create an instance of UpdateReminderRequest from a dict
update_reminder_request_from_dict = UpdateReminderRequest.from_dict(update_reminder_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


