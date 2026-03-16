# FileLinkReadModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** | File link id | [optional] 
**type** | **str** |  | [optional] 
**created_at** | **datetime** | Time of creation | [optional] 
**updated_at** | **datetime** | Time of the most recent change to the file link | [optional] 
**origin_data** | [**FileLinkOriginDataModel**](FileLinkOriginDataModel.md) |  | [optional] 
**embedded** | [**FileLinkReadModelEmbedded**](FileLinkReadModelEmbedded.md) |  | [optional] 
**links** | [**FileLinkReadModelLinks**](FileLinkReadModelLinks.md) |  | [optional] 

## Example

```python
from openproject_client.models.file_link_read_model import FileLinkReadModel

# TODO update the JSON string below
json = "{}"
# create an instance of FileLinkReadModel from a JSON string
file_link_read_model_instance = FileLinkReadModel.from_json(json)
# print the JSON string representation of the object
print(FileLinkReadModel.to_json())

# convert the object into a dict
file_link_read_model_dict = file_link_read_model_instance.to_dict()
# create an instance of FileLinkReadModel from a dict
file_link_read_model_from_dict = FileLinkReadModel.from_dict(file_link_read_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


