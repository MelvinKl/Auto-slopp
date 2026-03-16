# WeekDayModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**day** | **int** | The week day from 1 to 7. 1 is Monday. 7 is Sunday. | [readonly] 
**name** | **str** | The week day name. | 
**working** | **bool** | &#x60;true&#x60; for a working week day, &#x60;false&#x60; otherwise. | 
**links** | [**WeekDaySelfLinkModel**](WeekDaySelfLinkModel.md) |  | [optional] 

## Example

```python
from auto_slopp.openproject.openapi_client.models.week_day_model import WeekDayModel

# TODO update the JSON string below
json = "{}"
# create an instance of WeekDayModel from a JSON string
week_day_model_instance = WeekDayModel.from_json(json)
# print the JSON string representation of the object
print(WeekDayModel.to_json())

# convert the object into a dict
week_day_model_dict = week_day_model_instance.to_dict()
# create an instance of WeekDayModel from a dict
week_day_model_from_dict = WeekDayModel.from_dict(week_day_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


