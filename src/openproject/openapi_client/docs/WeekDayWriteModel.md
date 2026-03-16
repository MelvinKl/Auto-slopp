# WeekDayWriteModel

Describes a week day as a working day or a non-working day (weekend).

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**working** | **bool** | &#x60;true&#x60; for a working day. &#x60;false&#x60; for a weekend day. | 

## Example

```python
from openproject_client.models.week_day_write_model import WeekDayWriteModel

# TODO update the JSON string below
json = "{}"
# create an instance of WeekDayWriteModel from a JSON string
week_day_write_model_instance = WeekDayWriteModel.from_json(json)
# print the JSON string representation of the object
print(WeekDayWriteModel.to_json())

# convert the object into a dict
week_day_write_model_dict = week_day_write_model_instance.to_dict()
# create an instance of WeekDayWriteModel from a dict
week_day_write_model_from_dict = WeekDayWriteModel.from_dict(week_day_write_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


