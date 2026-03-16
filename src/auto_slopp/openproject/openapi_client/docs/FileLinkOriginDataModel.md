# FileLinkOriginDataModel


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

## Example

```python
from auto_slopp.openproject.openapi_client.models.file_link_origin_data_model import FileLinkOriginDataModel

# TODO update the JSON string below
json = "{}"
# create an instance of FileLinkOriginDataModel from a JSON string
file_link_origin_data_model_instance = FileLinkOriginDataModel.from_json(json)
# print the JSON string representation of the object
print(FileLinkOriginDataModel.to_json())

# convert the object into a dict
file_link_origin_data_model_dict = file_link_origin_data_model_instance.to_dict()
# create an instance of FileLinkOriginDataModel from a dict
file_link_origin_data_model_from_dict = FileLinkOriginDataModel.from_dict(file_link_origin_data_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


