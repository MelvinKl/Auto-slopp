# ActivityModelEmbedded


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**attachments** | [**AttachmentsModel**](AttachmentsModel.md) | Collection of attachments for this activity | [optional] 
**work_package** | [**WorkPackageModel**](WorkPackageModel.md) | The work package this activity belongs to  # Conditions  Only embedded when the &#x60;journable&#x60; of the activity is a work package | [optional] 
**emoji_reactions** | [**EmojiReactionsModel**](EmojiReactionsModel.md) | Collection of emoji reactions for this activity | [optional] 

## Example

```python
from auto_slopp.openproject.openapi_client.models.activity_model_embedded import ActivityModelEmbedded

# TODO update the JSON string below
json = "{}"
# create an instance of ActivityModelEmbedded from a JSON string
activity_model_embedded_instance = ActivityModelEmbedded.from_json(json)
# print the JSON string representation of the object
print(ActivityModelEmbedded.to_json())

# convert the object into a dict
activity_model_embedded_dict = activity_model_embedded_instance.to_dict()
# create an instance of ActivityModelEmbedded from a dict
activity_model_embedded_from_dict = ActivityModelEmbedded.from_dict(activity_model_embedded_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


