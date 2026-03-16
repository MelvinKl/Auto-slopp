# AttachmentsModelAllOfEmbeddedElements

Collection of Attachments

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
from openproject_client.models.attachments_model_all_of_embedded_elements import AttachmentsModelAllOfEmbeddedElements

# TODO update the JSON string below
json = "{}"
# create an instance of AttachmentsModelAllOfEmbeddedElements from a JSON string
attachments_model_all_of_embedded_elements_instance = AttachmentsModelAllOfEmbeddedElements.from_json(json)
# print the JSON string representation of the object
print(AttachmentsModelAllOfEmbeddedElements.to_json())

# convert the object into a dict
attachments_model_all_of_embedded_elements_dict = attachments_model_all_of_embedded_elements_instance.to_dict()
# create an instance of AttachmentsModelAllOfEmbeddedElements from a dict
attachments_model_all_of_embedded_elements_from_dict = AttachmentsModelAllOfEmbeddedElements.from_dict(attachments_model_all_of_embedded_elements_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


