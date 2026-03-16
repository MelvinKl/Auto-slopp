# NotificationModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | [optional] 
**id** | **int** | Notification id | [optional] 
**reason** | **str** | The reason for the notification | [optional] 
**read_ian** | **bool** | Whether the notification is marked as read | [optional] 
**details** | [**List[ValuesPropertyModel]**](ValuesPropertyModel.md) | A list of objects including detailed information about the notification. | [optional] 
**created_at** | **datetime** | The time the notification was created at | [optional] 
**updated_at** | **datetime** | The time the notification was last updated | [optional] 
**embedded** | [**NotificationModelEmbedded**](NotificationModelEmbedded.md) |  | [optional] 
**links** | [**NotificationModelLinks**](NotificationModelLinks.md) |  | [optional] 

## Example

```python
from openproject_client.models.notification_model import NotificationModel

# TODO update the JSON string below
json = "{}"
# create an instance of NotificationModel from a JSON string
notification_model_instance = NotificationModel.from_json(json)
# print the JSON string representation of the object
print(NotificationModel.to_json())

# convert the object into a dict
notification_model_dict = notification_model_instance.to_dict()
# create an instance of NotificationModel from a dict
notification_model_from_dict = NotificationModel.from_dict(notification_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


