# DocumentModelLinks


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_self** | [**Link**](Link.md) | This document  **Resource**: Document | [readonly] 
**project** | [**Link**](Link.md) | The project the document is in  **Resource**: Project | 
**attachments** | [**Link**](Link.md) | The attachments belonging to the document  **Resource**: []Attachment | 

## Example

```python
from openproject_client.models.document_model_links import DocumentModelLinks

# TODO update the JSON string below
json = "{}"
# create an instance of DocumentModelLinks from a JSON string
document_model_links_instance = DocumentModelLinks.from_json(json)
# print the JSON string representation of the object
print(DocumentModelLinks.to_json())

# convert the object into a dict
document_model_links_dict = document_model_links_instance.to_dict()
# create an instance of DocumentModelLinks from a dict
document_model_links_from_dict = DocumentModelLinks.from_dict(document_model_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


