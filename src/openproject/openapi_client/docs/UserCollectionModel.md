# UserCollectionModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**total** | **int** | The total amount of elements available in the collection. | 
**count** | **int** | Actual amount of elements in this response. | 
**links** | [**UserCollectionModelAllOfLinks**](UserCollectionModelAllOfLinks.md) |  | 
**embedded** | [**UserCollectionModelAllOfEmbedded**](UserCollectionModelAllOfEmbedded.md) |  | 

## Example

```python
from openproject_client.models.user_collection_model import UserCollectionModel

# TODO update the JSON string below
json = "{}"
# create an instance of UserCollectionModel from a JSON string
user_collection_model_instance = UserCollectionModel.from_json(json)
# print the JSON string representation of the object
print(UserCollectionModel.to_json())

# convert the object into a dict
user_collection_model_dict = user_collection_model_instance.to_dict()
# create an instance of UserCollectionModel from a dict
user_collection_model_from_dict = UserCollectionModel.from_dict(user_collection_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


