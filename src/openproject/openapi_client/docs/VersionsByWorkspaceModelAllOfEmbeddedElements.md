# VersionsByWorkspaceModelAllOfEmbeddedElements

Collection of Versions

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
from openproject_client.models.versions_by_workspace_model_all_of_embedded_elements import VersionsByWorkspaceModelAllOfEmbeddedElements

# TODO update the JSON string below
json = "{}"
# create an instance of VersionsByWorkspaceModelAllOfEmbeddedElements from a JSON string
versions_by_workspace_model_all_of_embedded_elements_instance = VersionsByWorkspaceModelAllOfEmbeddedElements.from_json(json)
# print the JSON string representation of the object
print(VersionsByWorkspaceModelAllOfEmbeddedElements.to_json())

# convert the object into a dict
versions_by_workspace_model_all_of_embedded_elements_dict = versions_by_workspace_model_all_of_embedded_elements_instance.to_dict()
# create an instance of VersionsByWorkspaceModelAllOfEmbeddedElements from a dict
versions_by_workspace_model_all_of_embedded_elements_from_dict = VersionsByWorkspaceModelAllOfEmbeddedElements.from_dict(versions_by_workspace_model_all_of_embedded_elements_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


