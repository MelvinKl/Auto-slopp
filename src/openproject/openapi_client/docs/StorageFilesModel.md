# StorageFilesModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**files** | [**List[StorageFileModel]**](StorageFileModel.md) | List of files provided by the selected storage. | 
**parent** | [**StorageFileModel**](StorageFileModel.md) | File of the currently selected parent directory. | 
**ancestors** | [**List[StorageFileModel]**](StorageFileModel.md) | List of ancestors of the parent directory. Can be empty, if parent directory was root directory. | 
**links** | [**StorageFileModelAllOfLinks**](StorageFileModelAllOfLinks.md) |  | 

## Example

```python
from openproject_client.models.storage_files_model import StorageFilesModel

# TODO update the JSON string below
json = "{}"
# create an instance of StorageFilesModel from a JSON string
storage_files_model_instance = StorageFilesModel.from_json(json)
# print the JSON string representation of the object
print(StorageFilesModel.to_json())

# convert the object into a dict
storage_files_model_dict = storage_files_model_instance.to_dict()
# create an instance of StorageFilesModel from a dict
storage_files_model_from_dict = StorageFilesModel.from_dict(storage_files_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


