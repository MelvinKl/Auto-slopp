# WeekDayCollectionWriteModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**embedded** | [**WeekDayCollectionWriteModelEmbedded**](WeekDayCollectionWriteModelEmbedded.md) |  | 

## Example

```python
from openproject_client.models.week_day_collection_write_model import WeekDayCollectionWriteModel

# TODO update the JSON string below
json = "{}"
# create an instance of WeekDayCollectionWriteModel from a JSON string
week_day_collection_write_model_instance = WeekDayCollectionWriteModel.from_json(json)
# print the JSON string representation of the object
print(WeekDayCollectionWriteModel.to_json())

# convert the object into a dict
week_day_collection_write_model_dict = week_day_collection_write_model_instance.to_dict()
# create an instance of WeekDayCollectionWriteModel from a dict
week_day_collection_write_model_from_dict = WeekDayCollectionWriteModel.from_dict(week_day_collection_write_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


