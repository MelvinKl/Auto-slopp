# EmojiReactionModelLinks


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_self** | [**Link**](Link.md) | This emoji reaction | [optional] 
**reactable** | [**Link**](Link.md) | The activity this emoji reaction belongs to | [optional] 
**reacting_users** | [**List[Link]**](Link.md) |  | [optional] 

## Example

```python
from openproject_client.models.emoji_reaction_model_links import EmojiReactionModelLinks

# TODO update the JSON string below
json = "{}"
# create an instance of EmojiReactionModelLinks from a JSON string
emoji_reaction_model_links_instance = EmojiReactionModelLinks.from_json(json)
# print the JSON string representation of the object
print(EmojiReactionModelLinks.to_json())

# convert the object into a dict
emoji_reaction_model_links_dict = emoji_reaction_model_links_instance.to_dict()
# create an instance of EmojiReactionModelLinks from a dict
emoji_reaction_model_links_from_dict = EmojiReactionModelLinks.from_dict(emoji_reaction_model_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


