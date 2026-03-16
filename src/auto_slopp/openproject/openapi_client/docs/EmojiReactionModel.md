# EmojiReactionModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | [optional] 
**id** | **str** | Emoji reaction id (format: reactable_id-reaction) | [optional] 
**reaction** | **str** | The reaction identifier | [optional] 
**emoji** | **str** | The emoji character | [optional] 
**reactions_count** | **int** | Number of users who reacted with this emoji | [optional] 
**first_reaction_at** | **datetime** | Time of the first reaction | [optional] 
**links** | [**EmojiReactionModelLinks**](EmojiReactionModelLinks.md) |  | [optional] 

## Example

```python
from auto_slopp.openproject.openapi_client.models.emoji_reaction_model import EmojiReactionModel

# TODO update the JSON string below
json = "{}"
# create an instance of EmojiReactionModel from a JSON string
emoji_reaction_model_instance = EmojiReactionModel.from_json(json)
# print the JSON string representation of the object
print(EmojiReactionModel.to_json())

# convert the object into a dict
emoji_reaction_model_dict = emoji_reaction_model_instance.to_dict()
# create an instance of EmojiReactionModel from a dict
emoji_reaction_model_from_dict = EmojiReactionModel.from_dict(emoji_reaction_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


