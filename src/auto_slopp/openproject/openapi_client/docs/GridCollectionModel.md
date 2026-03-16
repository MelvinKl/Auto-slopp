# GridCollectionModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**total** | **int** | The total amount of elements available in the collection. | 
**count** | **int** | Actual amount of elements in this response. | 
**links** | [**PaginatedCollectionModelAllOfLinks**](PaginatedCollectionModelAllOfLinks.md) |  | 
**page_size** | **int** | Amount of elements that a response will hold. | 
**offset** | **int** | The page number that is requested from paginated collection. | 
**embedded** | [**GridCollectionModelAllOfEmbedded**](GridCollectionModelAllOfEmbedded.md) |  | 

## Example

```python
from auto_slopp.openproject.openapi_client.models.grid_collection_model import GridCollectionModel

# TODO update the JSON string below
json = "{}"
# create an instance of GridCollectionModel from a JSON string
grid_collection_model_instance = GridCollectionModel.from_json(json)
# print the JSON string representation of the object
print(GridCollectionModel.to_json())

# convert the object into a dict
grid_collection_model_dict = grid_collection_model_instance.to_dict()
# create an instance of GridCollectionModel from a dict
grid_collection_model_from_dict = GridCollectionModel.from_dict(grid_collection_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


