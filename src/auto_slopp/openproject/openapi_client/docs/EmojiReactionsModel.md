# EmojiReactionsModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | [optional] 
**total** | **int** | Total number of emoji reactions | [optional] 
**count** | **int** | Number of emoji reactions in this response | [optional] 
**embedded** | [**EmojiReactionsModelEmbedded**](EmojiReactionsModelEmbedded.md) |  | [optional] 
**links** | [**EmojiReactionsModelLinks**](EmojiReactionsModelLinks.md) |  | [optional] 

## Example

```python
from auto_slopp.openproject.openapi_client.models.emoji_reactions_model import EmojiReactionsModel

# TODO update the JSON string below
json = "{}"
# create an instance of EmojiReactionsModel from a JSON string
emoji_reactions_model_instance = EmojiReactionsModel.from_json(json)
# print the JSON string representation of the object
print(EmojiReactionsModel.to_json())

# convert the object into a dict
emoji_reactions_model_dict = emoji_reactions_model_instance.to_dict()
# create an instance of EmojiReactionsModel from a dict
emoji_reactions_model_from_dict = EmojiReactionsModel.from_dict(emoji_reactions_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


