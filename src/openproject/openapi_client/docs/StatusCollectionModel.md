# StatusCollectionModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**total** | **int** | The total amount of elements available in the collection. | 
**count** | **int** | Actual amount of elements in this response. | 
**links** | [**CollectionLinks**](CollectionLinks.md) |  | 
**embedded** | [**StatusCollectionModelAllOfEmbedded**](StatusCollectionModelAllOfEmbedded.md) |  | 

## Example

```python
from openproject_client.models.status_collection_model import StatusCollectionModel

# TODO update the JSON string below
json = "{}"
# create an instance of StatusCollectionModel from a JSON string
status_collection_model_instance = StatusCollectionModel.from_json(json)
# print the JSON string representation of the object
print(StatusCollectionModel.to_json())

# convert the object into a dict
status_collection_model_dict = status_collection_model_instance.to_dict()
# create an instance of StatusCollectionModel from a dict
status_collection_model_from_dict = StatusCollectionModel.from_dict(status_collection_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


