# PlaceholderUserCollectionModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**total** | **int** | The total amount of elements available in the collection. | 
**count** | **int** | Actual amount of elements in this response. | 
**links** | [**PlaceholderUserCollectionModelAllOfLinks**](PlaceholderUserCollectionModelAllOfLinks.md) |  | 
**embedded** | [**PlaceholderUserCollectionModelAllOfEmbedded**](PlaceholderUserCollectionModelAllOfEmbedded.md) |  | 

## Example

```python
from openproject_client.models.placeholder_user_collection_model import PlaceholderUserCollectionModel

# TODO update the JSON string below
json = "{}"
# create an instance of PlaceholderUserCollectionModel from a JSON string
placeholder_user_collection_model_instance = PlaceholderUserCollectionModel.from_json(json)
# print the JSON string representation of the object
print(PlaceholderUserCollectionModel.to_json())

# convert the object into a dict
placeholder_user_collection_model_dict = placeholder_user_collection_model_instance.to_dict()
# create an instance of PlaceholderUserCollectionModel from a dict
placeholder_user_collection_model_from_dict = PlaceholderUserCollectionModel.from_dict(placeholder_user_collection_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


