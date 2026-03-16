# CollectionModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**total** | **int** | The total amount of elements available in the collection. | 
**count** | **int** | Actual amount of elements in this response. | 
**links** | [**CollectionLinks**](CollectionLinks.md) |  | 

## Example

```python
from auto_slopp.openproject.openapi_client.models.collection_model import CollectionModel

# TODO update the JSON string below
json = "{}"
# create an instance of CollectionModel from a JSON string
collection_model_instance = CollectionModel.from_json(json)
# print the JSON string representation of the object
print(CollectionModel.to_json())

# convert the object into a dict
collection_model_dict = collection_model_instance.to_dict()
# create an instance of CollectionModel from a dict
collection_model_from_dict = CollectionModel.from_dict(collection_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


