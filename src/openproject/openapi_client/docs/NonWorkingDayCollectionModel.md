# NonWorkingDayCollectionModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**total** | **int** | The total amount of elements available in the collection. | 
**count** | **int** | Actual amount of elements in this response. | 
**links** | [**NonWorkingDayCollectionModelAllOfLinks**](NonWorkingDayCollectionModelAllOfLinks.md) |  | 
**embedded** | [**NonWorkingDayCollectionModelAllOfEmbedded**](NonWorkingDayCollectionModelAllOfEmbedded.md) |  | 

## Example

```python
from openproject_client.models.non_working_day_collection_model import NonWorkingDayCollectionModel

# TODO update the JSON string below
json = "{}"
# create an instance of NonWorkingDayCollectionModel from a JSON string
non_working_day_collection_model_instance = NonWorkingDayCollectionModel.from_json(json)
# print the JSON string representation of the object
print(NonWorkingDayCollectionModel.to_json())

# convert the object into a dict
non_working_day_collection_model_dict = non_working_day_collection_model_instance.to_dict()
# create an instance of NonWorkingDayCollectionModel from a dict
non_working_day_collection_model_from_dict = NonWorkingDayCollectionModel.from_dict(non_working_day_collection_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


