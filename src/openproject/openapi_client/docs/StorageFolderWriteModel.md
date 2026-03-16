# StorageFolderWriteModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Name of the folder to be created | 
**parent_id** | **str** | Unique identifier of the parent folder in which the new folder should be created in | 

## Example

```python
from openproject_client.models.storage_folder_write_model import StorageFolderWriteModel

# TODO update the JSON string below
json = "{}"
# create an instance of StorageFolderWriteModel from a JSON string
storage_folder_write_model_instance = StorageFolderWriteModel.from_json(json)
# print the JSON string representation of the object
print(StorageFolderWriteModel.to_json())

# convert the object into a dict
storage_folder_write_model_dict = storage_folder_write_model_instance.to_dict()
# create an instance of StorageFolderWriteModel from a dict
storage_folder_write_model_from_dict = StorageFolderWriteModel.from_dict(storage_folder_write_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


