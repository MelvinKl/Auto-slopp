# DayCollectionModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**total** | **int** | The total amount of elements available in the collection. | 
**count** | **int** | Actual amount of elements in this response. | 
**links** | [**DayCollectionModelAllOfLinks**](DayCollectionModelAllOfLinks.md) |  | 
**embedded** | [**DayCollectionModelAllOfEmbedded**](DayCollectionModelAllOfEmbedded.md) |  | 

## Example

```python
from openproject_client.models.day_collection_model import DayCollectionModel

# TODO update the JSON string below
json = "{}"
# create an instance of DayCollectionModel from a JSON string
day_collection_model_instance = DayCollectionModel.from_json(json)
# print the JSON string representation of the object
print(DayCollectionModel.to_json())

# convert the object into a dict
day_collection_model_dict = day_collection_model_instance.to_dict()
# create an instance of DayCollectionModel from a dict
day_collection_model_from_dict = DayCollectionModel.from_dict(day_collection_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


