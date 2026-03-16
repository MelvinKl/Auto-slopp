# WeekDayCollectionModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**total** | **int** | The total amount of elements available in the collection. | 
**count** | **int** | Actual amount of elements in this response. | 
**links** | [**WeekDayCollectionModelAllOfLinks**](WeekDayCollectionModelAllOfLinks.md) |  | 
**embedded** | [**WeekDayCollectionModelAllOfEmbedded**](WeekDayCollectionModelAllOfEmbedded.md) |  | 

## Example

```python
from auto_slopp.openproject.openapi_client.models.week_day_collection_model import WeekDayCollectionModel

# TODO update the JSON string below
json = "{}"
# create an instance of WeekDayCollectionModel from a JSON string
week_day_collection_model_instance = WeekDayCollectionModel.from_json(json)
# print the JSON string representation of the object
print(WeekDayCollectionModel.to_json())

# convert the object into a dict
week_day_collection_model_dict = week_day_collection_model_instance.to_dict()
# create an instance of WeekDayCollectionModel from a dict
week_day_collection_model_from_dict = WeekDayCollectionModel.from_dict(week_day_collection_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


