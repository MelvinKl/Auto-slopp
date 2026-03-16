# PaginatedCollectionModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**total** | **int** | The total amount of elements available in the collection. | 
**count** | **int** | Actual amount of elements in this response. | 
**links** | [**PaginatedCollectionModelAllOfLinks**](PaginatedCollectionModelAllOfLinks.md) |  | 
**page_size** | **int** | Amount of elements that a response will hold. | 
**offset** | **int** | The page number that is requested from paginated collection. | 

## Example

```python
from openproject_client.models.paginated_collection_model import PaginatedCollectionModel

# TODO update the JSON string below
json = "{}"
# create an instance of PaginatedCollectionModel from a JSON string
paginated_collection_model_instance = PaginatedCollectionModel.from_json(json)
# print the JSON string representation of the object
print(PaginatedCollectionModel.to_json())

# convert the object into a dict
paginated_collection_model_dict = paginated_collection_model_instance.to_dict()
# create an instance of PaginatedCollectionModel from a dict
paginated_collection_model_from_dict = PaginatedCollectionModel.from_dict(paginated_collection_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


