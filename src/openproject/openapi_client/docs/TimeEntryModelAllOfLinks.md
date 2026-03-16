# TimeEntryModelAllOfLinks


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_self** | [**Link**](Link.md) | This time entry  **Resource**: TimeEntry | 
**update_immediately** | [**Link**](Link.md) | Directly perform edits on this time entry  # Conditions  **Permission**: &#39;edit time entries&#39; or &#39;edit own time entries&#39; if the time entry belongs to the user | [optional] 
**update** | [**Link**](Link.md) | Form endpoint that aids in preparing and performing edits on a TimeEntry  # Conditions  **Permission**: &#39;edit time entries&#39; or &#39;edit own time entries&#39; if the time entry belongs to the user | [optional] 
**delete** | [**Link**](Link.md) | Delete this time entry  # Conditions  **Permission**: &#39;edit time entries&#39; or &#39;edit own time entries&#39; if the time entry belongs to the user | [optional] 
**var_schema** | [**Link**](Link.md) | The time entry schema  **Resource**: Schema | [optional] 
**project** | [**Link**](Link.md) | The project the time entry is bundled in. The project might be different from the work package&#39;s project once the workPackage is moved.  **Resource**: Project | 
**entity** | [**Link**](Link.md) | The entity the time entry is created on  **Resource**: WorkPackage, Meeting | 
**user** | [**Link**](Link.md) | The user the time entry tracks expenditures for  **Resource**: User | 
**activity** | [**Link**](Link.md) | The time entry activity the time entry is categorized as  **Resource**: TimeEntriesActivity | 

## Example

```python
from openproject_client.models.time_entry_model_all_of_links import TimeEntryModelAllOfLinks

# TODO update the JSON string below
json = "{}"
# create an instance of TimeEntryModelAllOfLinks from a JSON string
time_entry_model_all_of_links_instance = TimeEntryModelAllOfLinks.from_json(json)
# print the JSON string representation of the object
print(TimeEntryModelAllOfLinks.to_json())

# convert the object into a dict
time_entry_model_all_of_links_dict = time_entry_model_all_of_links_instance.to_dict()
# create an instance of TimeEntryModelAllOfLinks from a dict
time_entry_model_all_of_links_from_dict = TimeEntryModelAllOfLinks.from_dict(time_entry_model_all_of_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


