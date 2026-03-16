# VersionWriteModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Version name | [optional] 
**description** | [**Formattable**](Formattable.md) |  | [optional] 
**start_date** | **date** |  | [optional] 
**end_date** | **date** |  | [optional] 
**status** | **str** | The current status of the version. This could be:  - *open*: if the version is available to be assigned to work packages in all shared projects - *locked*: if the version is not finished, but locked for further assignments to work packages - *closed*: if the version is finished | [optional] 
**sharing** | **str** | The indicator of how the version is shared between projects. This could be:  - *none*: if the version is only available in the defining project - *descendants*: if the version is shared with the descendants of the defining project - *hierarchy*: if the version is shared with the descendants and the ancestors of the defining project - *tree*: if the version is shared with the root project of the defining project and all descendants of the root project - *system*: if the version is shared globally | [optional] 
**links** | [**VersionWriteModelAllOfLinks**](VersionWriteModelAllOfLinks.md) |  | [optional] 

## Example

```python
from openproject_client.models.version_write_model import VersionWriteModel

# TODO update the JSON string below
json = "{}"
# create an instance of VersionWriteModel from a JSON string
version_write_model_instance = VersionWriteModel.from_json(json)
# print the JSON string representation of the object
print(VersionWriteModel.to_json())

# convert the object into a dict
version_write_model_dict = version_write_model_instance.to_dict()
# create an instance of VersionWriteModel from a dict
version_write_model_from_dict = VersionWriteModel.from_dict(version_write_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


