# StorageCollectionModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**total** | **int** | The total amount of elements available in the collection. | 
**count** | **int** | Actual amount of elements in this response. | 
**links** | [**StorageCollectionModelAllOfLinks**](StorageCollectionModelAllOfLinks.md) |  | 
**embedded** | [**StorageCollectionModelAllOfEmbedded**](StorageCollectionModelAllOfEmbedded.md) |  | 

## Example

```python
from openproject_client.models.storage_collection_model import StorageCollectionModel

# TODO update the JSON string below
json = "{}"
# create an instance of StorageCollectionModel from a JSON string
storage_collection_model_instance = StorageCollectionModel.from_json(json)
# print the JSON string representation of the object
print(StorageCollectionModel.to_json())

# convert the object into a dict
storage_collection_model_dict = storage_collection_model_instance.to_dict()
# create an instance of StorageCollectionModel from a dict
storage_collection_model_from_dict = StorageCollectionModel.from_dict(storage_collection_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


