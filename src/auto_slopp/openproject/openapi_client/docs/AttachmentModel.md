# AttachmentModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** | Attachment&#39;s id | [optional] 
**file_name** | **str** | The name of the uploaded file | 
**file_size** | **int** | The size of the uploaded file in Bytes | [optional] 
**description** | [**Formattable**](Formattable.md) | A user provided description of the file | 
**status** | **str** |  | 
**content_type** | **str** | The files MIME-Type as determined by the server | 
**digest** | [**AttachmentModelDigest**](AttachmentModelDigest.md) |  | 
**created_at** | **datetime** | Time of creation | 
**links** | [**AttachmentModelLinks**](AttachmentModelLinks.md) |  | [optional] 

## Example

```python
from auto_slopp.openproject.openapi_client.models.attachment_model import AttachmentModel

# TODO update the JSON string below
json = "{}"
# create an instance of AttachmentModel from a JSON string
attachment_model_instance = AttachmentModel.from_json(json)
# print the JSON string representation of the object
print(AttachmentModel.to_json())

# convert the object into a dict
attachment_model_dict = attachment_model_instance.to_dict()
# create an instance of AttachmentModel from a dict
attachment_model_from_dict = AttachmentModel.from_dict(attachment_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


