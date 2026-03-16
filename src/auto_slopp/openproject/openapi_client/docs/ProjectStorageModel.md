# ProjectStorageModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**id** | **int** | The project storage&#39;s id | 
**project_folder_mode** | **str** |  | 
**created_at** | **datetime** | Time of creation | 
**updated_at** | **datetime** | Time of the most recent change to the project storage | 
**links** | [**ProjectStorageModelLinks**](ProjectStorageModelLinks.md) |  | [optional] 

## Example

```python
from auto_slopp.openproject.openapi_client.models.project_storage_model import ProjectStorageModel

# TODO update the JSON string below
json = "{}"
# create an instance of ProjectStorageModel from a JSON string
project_storage_model_instance = ProjectStorageModel.from_json(json)
# print the JSON string representation of the object
print(ProjectStorageModel.to_json())

# convert the object into a dict
project_storage_model_dict = project_storage_model_instance.to_dict()
# create an instance of ProjectStorageModel from a dict
project_storage_model_from_dict = ProjectStorageModel.from_dict(project_storage_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


