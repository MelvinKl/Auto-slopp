# ToggleActivityEmojiReactionRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**reaction** | **str** | The emoji reaction identifier | 

## Example

```python
from auto_slopp.openproject.openapi_client.models.toggle_activity_emoji_reaction_request import ToggleActivityEmojiReactionRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ToggleActivityEmojiReactionRequest from a JSON string
toggle_activity_emoji_reaction_request_instance = ToggleActivityEmojiReactionRequest.from_json(json)
# print the JSON string representation of the object
print(ToggleActivityEmojiReactionRequest.to_json())

# convert the object into a dict
toggle_activity_emoji_reaction_request_dict = toggle_activity_emoji_reaction_request_instance.to_dict()
# create an instance of ToggleActivityEmojiReactionRequest from a dict
toggle_activity_emoji_reaction_request_from_dict = ToggleActivityEmojiReactionRequest.from_dict(toggle_activity_emoji_reaction_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


