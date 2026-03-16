# MeetingModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** | Identifier of this meeting | [readonly] 
**title** | **str** | The meeting&#39;s title | 
**location** | **str** | The meeting&#39;s location | [optional] 
**lock_version** | **int** | The version of the item as used for optimistic locking | [readonly] 
**start_time** | **datetime** | The scheduled meeting start time. | 
**end_time** | **datetime** | The scheduled meeting start time. | 
**duration** | **float** | The meeting duration in minutes. | 
**created_at** | **datetime** | Time of creation. Can be writable by admins with the &#x60;apiv3_write_readonly_attributes&#x60; setting enabled. | [readonly] 
**updated_at** | **datetime** | Time of the most recent change to the meeting. | [readonly] 
**links** | [**MeetingModelLinks**](MeetingModelLinks.md) |  | [optional] 

## Example

```python
from auto_slopp.openproject.openapi_client.models.meeting_model import MeetingModel

# TODO update the JSON string below
json = "{}"
# create an instance of MeetingModel from a JSON string
meeting_model_instance = MeetingModel.from_json(json)
# print the JSON string representation of the object
print(MeetingModel.to_json())

# convert the object into a dict
meeting_model_dict = meeting_model_instance.to_dict()
# create an instance of MeetingModel from a dict
meeting_model_from_dict = MeetingModel.from_dict(meeting_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


