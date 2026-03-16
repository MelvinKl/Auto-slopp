# StorageFileUploadPreparationModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**project_id** | **int** | The project identifier, from where a user starts uploading a file. | 
**file_name** | **str** | The file name. | 
**parent** | **str** | The directory to which the file is to be uploaded. For root directories, the value &#x60;/&#x60; must be provided. | 

## Example

```python
from openproject_client.models.storage_file_upload_preparation_model import StorageFileUploadPreparationModel

# TODO update the JSON string below
json = "{}"
# create an instance of StorageFileUploadPreparationModel from a JSON string
storage_file_upload_preparation_model_instance = StorageFileUploadPreparationModel.from_json(json)
# print the JSON string representation of the object
print(StorageFileUploadPreparationModel.to_json())

# convert the object into a dict
storage_file_upload_preparation_model_dict = storage_file_upload_preparation_model_instance.to_dict()
# create an instance of StorageFileUploadPreparationModel from a dict
storage_file_upload_preparation_model_from_dict = StorageFileUploadPreparationModel.from_dict(storage_file_upload_preparation_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


