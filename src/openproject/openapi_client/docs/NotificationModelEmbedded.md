# NotificationModelEmbedded


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**actor** | [**UserModel**](UserModel.md) |  | [optional] 
**project** | [**MembershipReadModelEmbeddedProject**](MembershipReadModelEmbeddedProject.md) |  | 
**activity** | [**ActivityModel**](ActivityModel.md) |  | [optional] 
**resource** | [**WorkPackageModel**](WorkPackageModel.md) |  | 

## Example

```python
from openproject_client.models.notification_model_embedded import NotificationModelEmbedded

# TODO update the JSON string below
json = "{}"
# create an instance of NotificationModelEmbedded from a JSON string
notification_model_embedded_instance = NotificationModelEmbedded.from_json(json)
# print the JSON string representation of the object
print(NotificationModelEmbedded.to_json())

# convert the object into a dict
notification_model_embedded_dict = notification_model_embedded_instance.to_dict()
# create an instance of NotificationModelEmbedded from a dict
notification_model_embedded_from_dict = NotificationModelEmbedded.from_dict(notification_model_embedded_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


