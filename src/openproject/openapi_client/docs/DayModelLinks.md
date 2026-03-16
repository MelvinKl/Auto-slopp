# DayModelLinks


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_self** | [**Link**](Link.md) |  | 
**non_working_reasons** | [**List[Link]**](Link.md) | A list of resources describing why this day is a non-working day. Linked resources can be &#x60;NonWorkingDay&#x60; and &#x60;WeekDay&#x60; resources. This property is absent for working days. | [optional] 
**week_day** | [**Link**](Link.md) | The week day for this day. | [optional] 

## Example

```python
from openproject_client.models.day_model_links import DayModelLinks

# TODO update the JSON string below
json = "{}"
# create an instance of DayModelLinks from a JSON string
day_model_links_instance = DayModelLinks.from_json(json)
# print the JSON string representation of the object
print(DayModelLinks.to_json())

# convert the object into a dict
day_model_links_dict = day_model_links_instance.to_dict()
# create an instance of DayModelLinks from a dict
day_model_links_from_dict = DayModelLinks.from_dict(day_model_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


