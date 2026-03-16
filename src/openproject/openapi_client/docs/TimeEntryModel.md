# TimeEntryModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** | The id of the time entry | [optional] 
**comment** | [**Formattable**](Formattable.md) | A comment to the time entry | [optional] 
**spent_on** | **date** | The date the expenditure is booked for | [optional] 
**hours** | **str** | The time quantifying the expenditure | [optional] 
**ongoing** | **bool** | Whether the time entry is actively tracking time | [optional] 
**created_at** | **datetime** | The time the time entry was created | [optional] 
**start_time** | **datetime** | The time the time entry was started, or null if the time entry does not have a start time.  The time is returned as UTC time, if presented to the user it should be converted to the user&#39;s timezone.  This field is only available if the global &#x60;allow_tracking_start_and_end_times&#x60; setting is enabled. | [optional] 
**end_time** | **datetime** | The time the time entry was ended, or null if the time entry does not have a start time.  The time is returned as UTC time, if presented to the user it should be converted to the user&#39;s timezone.  This field is only available if the global &#x60;allow_tracking_start_and_end_times&#x60; setting is enabled. | [optional] 
**updated_at** | **datetime** | The time the time entry was last updated | [optional] 
**links** | [**TimeEntryModelAllOfLinks**](TimeEntryModelAllOfLinks.md) |  | [optional] 

## Example

```python
from openproject_client.models.time_entry_model import TimeEntryModel

# TODO update the JSON string below
json = "{}"
# create an instance of TimeEntryModel from a JSON string
time_entry_model_instance = TimeEntryModel.from_json(json)
# print the JSON string representation of the object
print(TimeEntryModel.to_json())

# convert the object into a dict
time_entry_model_dict = time_entry_model_instance.to_dict()
# create an instance of TimeEntryModel from a dict
time_entry_model_from_dict = TimeEntryModel.from_dict(time_entry_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


