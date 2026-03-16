# ProjectStorageCollectionModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**total** | **int** | The total amount of elements available in the collection. | 
**count** | **int** | Actual amount of elements in this response. | 
**links** | [**ProjectStorageCollectionModelAllOfLinks**](ProjectStorageCollectionModelAllOfLinks.md) |  | 
**embedded** | [**ProjectStorageCollectionModelAllOfEmbedded**](ProjectStorageCollectionModelAllOfEmbedded.md) |  | 

## Example

```python
from openproject_client.models.project_storage_collection_model import ProjectStorageCollectionModel

# TODO update the JSON string below
json = "{}"
# create an instance of ProjectStorageCollectionModel from a JSON string
project_storage_collection_model_instance = ProjectStorageCollectionModel.from_json(json)
# print the JSON string representation of the object
print(ProjectStorageCollectionModel.to_json())

# convert the object into a dict
project_storage_collection_model_dict = project_storage_collection_model_instance.to_dict()
# create an instance of ProjectStorageCollectionModel from a dict
project_storage_collection_model_from_dict = ProjectStorageCollectionModel.from_dict(project_storage_collection_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


