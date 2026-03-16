# AttachmentsModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**total** | **int** | The total amount of elements available in the collection. | 
**count** | **int** | Actual amount of elements in this response. | 
**links** | [**AttachmentsModelAllOfLinks**](AttachmentsModelAllOfLinks.md) |  | 
**embedded** | [**AttachmentsModelAllOfEmbedded**](AttachmentsModelAllOfEmbedded.md) |  | 

## Example

```python
from auto_slopp.openproject.openapi_client.models.attachments_model import AttachmentsModel

# TODO update the JSON string below
json = "{}"
# create an instance of AttachmentsModel from a JSON string
attachments_model_instance = AttachmentsModel.from_json(json)
# print the JSON string representation of the object
print(AttachmentsModel.to_json())

# convert the object into a dict
attachments_model_dict = attachments_model_instance.to_dict()
# create an instance of AttachmentsModel from a dict
attachments_model_from_dict = AttachmentsModel.from_dict(attachments_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


