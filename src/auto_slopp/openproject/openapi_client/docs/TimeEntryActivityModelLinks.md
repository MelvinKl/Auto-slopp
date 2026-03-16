# TimeEntryActivityModelLinks


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_self** | [**Link**](Link.md) | This time entry activity  **Resource**: TimeEntriesActivity | 
**projects** | [**List[Link]**](Link.md) |  | 

## Example

```python
from auto_slopp.openproject.openapi_client.models.time_entry_activity_model_links import TimeEntryActivityModelLinks

# TODO update the JSON string below
json = "{}"
# create an instance of TimeEntryActivityModelLinks from a JSON string
time_entry_activity_model_links_instance = TimeEntryActivityModelLinks.from_json(json)
# print the JSON string representation of the object
print(TimeEntryActivityModelLinks.to_json())

# convert the object into a dict
time_entry_activity_model_links_dict = time_entry_activity_model_links_instance.to_dict()
# create an instance of TimeEntryActivityModelLinks from a dict
time_entry_activity_model_links_from_dict = TimeEntryActivityModelLinks.from_dict(time_entry_activity_model_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


