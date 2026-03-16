# StorageFileUploadLinkModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**links** | [**StorageFileUploadLinkModelLinks**](StorageFileUploadLinkModelLinks.md) |  | 

## Example

```python
from auto_slopp.openproject.openapi_client.models.storage_file_upload_link_model import StorageFileUploadLinkModel

# TODO update the JSON string below
json = "{}"
# create an instance of StorageFileUploadLinkModel from a JSON string
storage_file_upload_link_model_instance = StorageFileUploadLinkModel.from_json(json)
# print the JSON string representation of the object
print(StorageFileUploadLinkModel.to_json())

# convert the object into a dict
storage_file_upload_link_model_dict = storage_file_upload_link_model_instance.to_dict()
# create an instance of StorageFileUploadLinkModel from a dict
storage_file_upload_link_model_from_dict = StorageFileUploadLinkModel.from_dict(storage_file_upload_link_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


