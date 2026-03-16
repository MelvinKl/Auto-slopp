# VersionsByWorkspaceModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**total** | **int** | The total amount of elements available in the collection. | 
**count** | **int** | Actual amount of elements in this response. | 
**links** | [**VersionsByWorkspaceModelAllOfLinks**](VersionsByWorkspaceModelAllOfLinks.md) |  | 
**embedded** | [**VersionsByWorkspaceModelAllOfEmbedded**](VersionsByWorkspaceModelAllOfEmbedded.md) |  | 

## Example

```python
from openproject_client.models.versions_by_workspace_model import VersionsByWorkspaceModel

# TODO update the JSON string below
json = "{}"
# create an instance of VersionsByWorkspaceModel from a JSON string
versions_by_workspace_model_instance = VersionsByWorkspaceModel.from_json(json)
# print the JSON string representation of the object
print(VersionsByWorkspaceModel.to_json())

# convert the object into a dict
versions_by_workspace_model_dict = versions_by_workspace_model_instance.to_dict()
# create an instance of VersionsByWorkspaceModel from a dict
versions_by_workspace_model_from_dict = VersionsByWorkspaceModel.from_dict(versions_by_workspace_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


