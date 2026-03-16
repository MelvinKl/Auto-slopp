# ReminderModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** | Reminder id | [optional] [readonly] 
**note** | **str** | The note of the reminder | [optional] 
**remind_at** | **datetime** | The date and time when the reminder is due | [optional] 
**links** | [**ReminderModelLinks**](ReminderModelLinks.md) |  | [optional] 

## Example

```python
from openproject_client.models.reminder_model import ReminderModel

# TODO update the JSON string below
json = "{}"
# create an instance of ReminderModel from a JSON string
reminder_model_instance = ReminderModel.from_json(json)
# print the JSON string representation of the object
print(ReminderModel.to_json())

# convert the object into a dict
reminder_model_dict = reminder_model_instance.to_dict()
# create an instance of ReminderModel from a dict
reminder_model_from_dict = ReminderModel.from_dict(reminder_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


