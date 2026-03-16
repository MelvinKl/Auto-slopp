# StorageFileModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | Linked file&#39;s id on the origin | 
**name** | **str** | Linked file&#39;s name on the origin | 
**mime_type** | **str** | MIME type of the linked file.  To link a folder entity, the custom MIME type &#x60;application/x-op-directory&#x60; MUST be provided. Otherwise it defaults back to an unknown MIME type. | [optional] 
**size** | **int** | file size on origin in bytes | [optional] 
**created_at** | **datetime** | Timestamp of the creation datetime of the file on the origin | [optional] 
**last_modified_at** | **datetime** | Timestamp of the datetime of the last modification of the file on the origin | [optional] 
**created_by_name** | **str** | Display name of the author that created the file on the origin | [optional] 
**last_modified_by_name** | **str** | Display name of the author that modified the file on the origin last | [optional] 
**type** | **str** |  | 
**location** | **str** | Location identification for file in storage | 
**links** | [**StorageFileModelAllOfLinks**](StorageFileModelAllOfLinks.md) |  | 

## Example

```python
from openproject_client.models.storage_file_model import StorageFileModel

# TODO update the JSON string below
json = "{}"
# create an instance of StorageFileModel from a JSON string
storage_file_model_instance = StorageFileModel.from_json(json)
# print the JSON string representation of the object
print(StorageFileModel.to_json())

# convert the object into a dict
storage_file_model_dict = storage_file_model_instance.to_dict()
# create an instance of StorageFileModel from a dict
storage_file_model_from_dict = StorageFileModel.from_dict(storage_file_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


