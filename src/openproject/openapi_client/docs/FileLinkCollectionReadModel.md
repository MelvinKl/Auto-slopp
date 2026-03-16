# FileLinkCollectionReadModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**total** | **int** | The total amount of elements available in the collection. | 
**count** | **int** | Actual amount of elements in this response. | 
**links** | [**FileLinkCollectionReadModelAllOfLinks**](FileLinkCollectionReadModelAllOfLinks.md) |  | 
**page_size** | **int** | Amount of elements that a response will hold. | 
**offset** | **int** | The page number that is requested from paginated collection. | 
**embedded** | [**FileLinkCollectionReadModelAllOfEmbedded**](FileLinkCollectionReadModelAllOfEmbedded.md) |  | [optional] 

## Example

```python
from openproject_client.models.file_link_collection_read_model import FileLinkCollectionReadModel

# TODO update the JSON string below
json = "{}"
# create an instance of FileLinkCollectionReadModel from a JSON string
file_link_collection_read_model_instance = FileLinkCollectionReadModel.from_json(json)
# print the JSON string representation of the object
print(FileLinkCollectionReadModel.to_json())

# convert the object into a dict
file_link_collection_read_model_dict = file_link_collection_read_model_instance.to_dict()
# create an instance of FileLinkCollectionReadModel from a dict
file_link_collection_read_model_from_dict = FileLinkCollectionReadModel.from_dict(file_link_collection_read_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


