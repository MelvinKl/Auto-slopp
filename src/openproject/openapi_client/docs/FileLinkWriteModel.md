# FileLinkWriteModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**origin_data** | [**FileLinkOriginDataModel**](FileLinkOriginDataModel.md) |  | 
**links** | [**FileLinkWriteModelLinks**](FileLinkWriteModelLinks.md) |  | 

## Example

```python
from openproject_client.models.file_link_write_model import FileLinkWriteModel

# TODO update the JSON string below
json = "{}"
# create an instance of FileLinkWriteModel from a JSON string
file_link_write_model_instance = FileLinkWriteModel.from_json(json)
# print the JSON string representation of the object
print(FileLinkWriteModel.to_json())

# convert the object into a dict
file_link_write_model_dict = file_link_write_model_instance.to_dict()
# create an instance of FileLinkWriteModel from a dict
file_link_write_model_from_dict = FileLinkWriteModel.from_dict(file_link_write_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


