# PriorityCollectionModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**total** | **int** | The total amount of elements available in the collection. | 
**count** | **int** | Actual amount of elements in this response. | 
**links** | [**PriorityCollectionModelAllOfLinks**](PriorityCollectionModelAllOfLinks.md) |  | 
**embedded** | [**PriorityCollectionModelAllOfEmbedded**](PriorityCollectionModelAllOfEmbedded.md) |  | 

## Example

```python
from openproject_client.models.priority_collection_model import PriorityCollectionModel

# TODO update the JSON string below
json = "{}"
# create an instance of PriorityCollectionModel from a JSON string
priority_collection_model_instance = PriorityCollectionModel.from_json(json)
# print the JSON string representation of the object
print(PriorityCollectionModel.to_json())

# convert the object into a dict
priority_collection_model_dict = priority_collection_model_instance.to_dict()
# create an instance of PriorityCollectionModel from a dict
priority_collection_model_from_dict = PriorityCollectionModel.from_dict(priority_collection_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


