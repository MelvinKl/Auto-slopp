# VersionReadModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** | Version id | 
**type** | **str** |  | 
**name** | **str** | Version name | 
**description** | [**Formattable**](Formattable.md) |  | 
**start_date** | **date** |  | 
**end_date** | **date** |  | 
**status** | **str** | The current status of the version. This could be:  - *open*: if the version is available to be assigned to work packages in all shared projects - *locked*: if the version is not finished, but locked for further assignments to work packages - *closed*: if the version is finished | 
**sharing** | **str** | The indicator of how the version is shared between projects. This could be:  - *none*: if the version is only available in the defining project - *descendants*: if the version is shared with the descendants of the defining project - *hierarchy*: if the version is shared with the descendants and the ancestors of the defining project - *tree*: if the version is shared with the root project of the defining project and all descendants of the root project - *system*: if the version is shared globally | 
**created_at** | **datetime** | Time of creation | 
**updated_at** | **datetime** | Time of the most recent change to the version | 
**links** | [**VersionReadModelAllOfLinks**](VersionReadModelAllOfLinks.md) |  | [optional] 

## Example

```python
from auto_slopp.openproject.openapi_client.models.version_read_model import VersionReadModel

# TODO update the JSON string below
json = "{}"
# create an instance of VersionReadModel from a JSON string
version_read_model_instance = VersionReadModel.from_json(json)
# print the JSON string representation of the object
print(VersionReadModel.to_json())

# convert the object into a dict
version_read_model_dict = version_read_model_instance.to_dict()
# create an instance of VersionReadModel from a dict
version_read_model_from_dict = VersionReadModel.from_dict(version_read_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


