# NotificationModelLinks


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_self** | [**Link**](Link.md) | This notification  **Resource**: Notification | 
**read_ian** | [**Link**](Link.md) | Request to mark the notification as read. Only available if the notification is currently unread. | [optional] 
**unread_ian** | [**Link**](Link.md) | Request to mark the notification as unread. Only available if the notification is currently read. | [optional] 
**project** | [**Link**](Link.md) | The workspace the notification originated in  **Resource**: Workspace | 
**actor** | [**Link**](Link.md) | The user that caused the notification. This might be null in case no user triggered the notification.  **Resource**: User | 
**resource** | [**Link**](Link.md) | The linked resource of the notification, if any.  **Resource**: Polymorphic | 
**activity** | [**Link**](Link.md) | The journal activity, if the notification originated from a journal entry. This might be null in case no activity triggered the notification.  **Resource**: Activity | 

## Example

```python
from openproject_client.models.notification_model_links import NotificationModelLinks

# TODO update the JSON string below
json = "{}"
# create an instance of NotificationModelLinks from a JSON string
notification_model_links_instance = NotificationModelLinks.from_json(json)
# print the JSON string representation of the object
print(NotificationModelLinks.to_json())

# convert the object into a dict
notification_model_links_dict = notification_model_links_instance.to_dict()
# create an instance of NotificationModelLinks from a dict
notification_model_links_from_dict = NotificationModelLinks.from_dict(notification_model_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


