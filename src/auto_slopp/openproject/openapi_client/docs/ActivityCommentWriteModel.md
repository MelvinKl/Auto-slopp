# ActivityCommentWriteModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**comment** | [**ActivityCommentWriteModelComment**](ActivityCommentWriteModelComment.md) |  | [optional] 
**internal** | **bool** | Determines whether this comment is internal. This is only available to users with &#x60;add_internal_comments&#x60; permission. It defaults to &#x60;false&#x60;, if unset. | [optional] [default to False]

## Example

```python
from auto_slopp.openproject.openapi_client.models.activity_comment_write_model import ActivityCommentWriteModel

# TODO update the JSON string below
json = "{}"
# create an instance of ActivityCommentWriteModel from a JSON string
activity_comment_write_model_instance = ActivityCommentWriteModel.from_json(json)
# print the JSON string representation of the object
print(ActivityCommentWriteModel.to_json())

# convert the object into a dict
activity_comment_write_model_dict = activity_comment_write_model_instance.to_dict()
# create an instance of ActivityCommentWriteModel from a dict
activity_comment_write_model_from_dict = ActivityCommentWriteModel.from_dict(activity_comment_write_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


