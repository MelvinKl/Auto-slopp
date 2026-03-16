# MeetingModelLinks


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_self** | [**Link**](Link.md) | This meeting  **Resource**: Meeting | [optional] [readonly] 
**author** | [**Link**](Link.md) | The user having created the meeting  **Resource**: User | [optional] [readonly] 
**project** | [**Link**](Link.md) | The project the meeting is in  **Resource**: Project | [optional] 
**attachments** | [**Link**](Link.md) | The attachment collection of this grid.  **Resource**: AttachmentCollection | [optional] 
**add_attachment** | [**Link**](Link.md) | Attach a file to the meeting  # Conditions  **Permission**: edit meeting | [optional] [readonly] 

## Example

```python
from auto_slopp.openproject.openapi_client.models.meeting_model_links import MeetingModelLinks

# TODO update the JSON string below
json = "{}"
# create an instance of MeetingModelLinks from a JSON string
meeting_model_links_instance = MeetingModelLinks.from_json(json)
# print the JSON string representation of the object
print(MeetingModelLinks.to_json())

# convert the object into a dict
meeting_model_links_dict = meeting_model_links_instance.to_dict()
# create an instance of MeetingModelLinks from a dict
meeting_model_links_from_dict = MeetingModelLinks.from_dict(meeting_model_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


