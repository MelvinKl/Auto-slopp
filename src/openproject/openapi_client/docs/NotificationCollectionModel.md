# NotificationCollectionModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**total** | **int** | The total amount of elements available in the collection. | 
**count** | **int** | Actual amount of elements in this response. | 
**links** | [**NotificationCollectionModelAllOfLinks**](NotificationCollectionModelAllOfLinks.md) |  | 
**embedded** | [**NotificationCollectionModelAllOfEmbedded**](NotificationCollectionModelAllOfEmbedded.md) |  | 

## Example

```python
from openproject_client.models.notification_collection_model import NotificationCollectionModel

# TODO update the JSON string below
json = "{}"
# create an instance of NotificationCollectionModel from a JSON string
notification_collection_model_instance = NotificationCollectionModel.from_json(json)
# print the JSON string representation of the object
print(NotificationCollectionModel.to_json())

# convert the object into a dict
notification_collection_model_dict = notification_collection_model_instance.to_dict()
# create an instance of NotificationCollectionModel from a dict
notification_collection_model_from_dict = NotificationCollectionModel.from_dict(notification_collection_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


