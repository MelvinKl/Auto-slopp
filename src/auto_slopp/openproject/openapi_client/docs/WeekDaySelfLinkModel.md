# WeekDaySelfLinkModel

Identify a particular week day by its href.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_self** | [**Link**](Link.md) | This week day resource link.  **Resource**: WeekDay | [optional] [readonly] 

## Example

```python
from auto_slopp.openproject.openapi_client.models.week_day_self_link_model import WeekDaySelfLinkModel

# TODO update the JSON string below
json = "{}"
# create an instance of WeekDaySelfLinkModel from a JSON string
week_day_self_link_model_instance = WeekDaySelfLinkModel.from_json(json)
# print the JSON string representation of the object
print(WeekDaySelfLinkModel.to_json())

# convert the object into a dict
week_day_self_link_model_dict = week_day_self_link_model_instance.to_dict()
# create an instance of WeekDaySelfLinkModel from a dict
week_day_self_link_model_from_dict = WeekDaySelfLinkModel.from_dict(week_day_self_link_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


