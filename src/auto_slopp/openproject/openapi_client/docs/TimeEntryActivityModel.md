# TimeEntryActivityModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**id** | **int** | Time entry id | 
**name** | **str** | The human readable name chosen for this activity | 
**position** | **int** | The rank the activity has in a list of activities | 
**default** | **bool** | Flag to signal whether this activity is the default activity | 
**embedded** | [**TimeEntryActivityModelEmbedded**](TimeEntryActivityModelEmbedded.md) |  | 
**links** | [**TimeEntryActivityModelLinks**](TimeEntryActivityModelLinks.md) |  | 

## Example

```python
from auto_slopp.openproject.openapi_client.models.time_entry_activity_model import TimeEntryActivityModel

# TODO update the JSON string below
json = "{}"
# create an instance of TimeEntryActivityModel from a JSON string
time_entry_activity_model_instance = TimeEntryActivityModel.from_json(json)
# print the JSON string representation of the object
print(TimeEntryActivityModel.to_json())

# convert the object into a dict
time_entry_activity_model_dict = time_entry_activity_model_instance.to_dict()
# create an instance of TimeEntryActivityModel from a dict
time_entry_activity_model_from_dict = TimeEntryActivityModel.from_dict(time_entry_activity_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


