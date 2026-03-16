# DocumentModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** | Document&#39;s id | [optional] [readonly] 
**title** | **str** | The title chosen for the document | [optional] 
**description** | [**Formattable**](Formattable.md) | A text describing the document | [optional] 
**created_at** | **datetime** | The time the document was created at | [optional] [readonly] 
**links** | [**DocumentModelLinks**](DocumentModelLinks.md) |  | [optional] 

## Example

```python
from auto_slopp.openproject.openapi_client.models.document_model import DocumentModel

# TODO update the JSON string below
json = "{}"
# create an instance of DocumentModel from a JSON string
document_model_instance = DocumentModel.from_json(json)
# print the JSON string representation of the object
print(DocumentModel.to_json())

# convert the object into a dict
document_model_dict = document_model_instance.to_dict()
# create an instance of DocumentModel from a dict
document_model_from_dict = DocumentModel.from_dict(document_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


