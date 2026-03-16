# NotificationCollectionModelAllOfLinks


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_self** | [**Link**](Link.md) | This notification collection  **Resource**: NotificationCollectionModel | 
**jump_to** | [**Link**](Link.md) | The notification collection at another offset  **Resource**: NotificationCollectionModel | [optional] 
**change_size** | [**Link**](Link.md) | The notification collection with another size  **Resource**: NotificationCollectionModel | [optional] 

## Example

```python
from auto_slopp.openproject.openapi_client.models.notification_collection_model_all_of_links import NotificationCollectionModelAllOfLinks

# TODO update the JSON string below
json = "{}"
# create an instance of NotificationCollectionModelAllOfLinks from a JSON string
notification_collection_model_all_of_links_instance = NotificationCollectionModelAllOfLinks.from_json(json)
# print the JSON string representation of the object
print(NotificationCollectionModelAllOfLinks.to_json())

# convert the object into a dict
notification_collection_model_all_of_links_dict = notification_collection_model_all_of_links_instance.to_dict()
# create an instance of NotificationCollectionModelAllOfLinks from a dict
notification_collection_model_all_of_links_from_dict = NotificationCollectionModelAllOfLinks.from_dict(notification_collection_model_all_of_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


