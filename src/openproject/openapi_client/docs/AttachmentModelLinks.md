# AttachmentModelLinks


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**delete** | [**Link**](Link.md) | Deletes this attachment  # Conditions  **Permission**: edit on attachment container or being the author for attachments without container | [optional] 
**var_self** | [**Link**](Link.md) | This attachment  **Resource**: Attachment | 
**container** | [**Link**](Link.md) | The object (e.g. WorkPackage) housing the attachment  **Resource**: Anything | 
**author** | [**Link**](Link.md) | The user who uploaded the attachment  **Resource**: User | 
**download_location** | [**Link**](Link.md) | Direct download link to the attachment  **Resource**: - | 

## Example

```python
from openproject_client.models.attachment_model_links import AttachmentModelLinks

# TODO update the JSON string below
json = "{}"
# create an instance of AttachmentModelLinks from a JSON string
attachment_model_links_instance = AttachmentModelLinks.from_json(json)
# print the JSON string representation of the object
print(AttachmentModelLinks.to_json())

# convert the object into a dict
attachment_model_links_dict = attachment_model_links_instance.to_dict()
# create an instance of AttachmentModelLinks from a dict
attachment_model_links_from_dict = AttachmentModelLinks.from_dict(attachment_model_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


