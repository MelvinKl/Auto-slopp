# NotificationCollectionModelAllOfEmbedded


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**elements** | [**List[NotificationModel]**](NotificationModel.md) |  | 
**details_schemas** | [**List[SchemaModel]**](SchemaModel.md) |  | 

## Example

```python
from openproject_client.models.notification_collection_model_all_of_embedded import NotificationCollectionModelAllOfEmbedded

# TODO update the JSON string below
json = "{}"
# create an instance of NotificationCollectionModelAllOfEmbedded from a JSON string
notification_collection_model_all_of_embedded_instance = NotificationCollectionModelAllOfEmbedded.from_json(json)
# print the JSON string representation of the object
print(NotificationCollectionModelAllOfEmbedded.to_json())

# convert the object into a dict
notification_collection_model_all_of_embedded_dict = notification_collection_model_all_of_embedded_instance.to_dict()
# create an instance of NotificationCollectionModelAllOfEmbedded from a dict
notification_collection_model_all_of_embedded_from_dict = NotificationCollectionModelAllOfEmbedded.from_dict(notification_collection_model_all_of_embedded_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


