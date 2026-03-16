# VersionReadModelAllOfLinks


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_self** | [**Link**](Link.md) | This version  **Resource**: Version | 
**var_schema** | [**Link**](Link.md) | The schema of this version  **Resource**: VersionSchema | 
**update** | [**Link**](Link.md) | Form endpoint that aids in preparing and performing edits on the version  # Conditions  **Permission**: manage versions | [optional] 
**delete** | [**Link**](Link.md) | Deletes this version  # Conditions  **Permission**: manage versions | [optional] 
**update_immediately** | [**Link**](Link.md) | Directly perform edits on the version  # Conditions  **Permission**: manage versions | [optional] 
**defining_project** | [**Link**](Link.md) | The workspace to which the version belongs  **Resource**: Workspace | 
**available_in_projects** | [**Link**](Link.md) | Workspaces where this version can be used  **Resource**: Workspace | 

## Example

```python
from openproject_client.models.version_read_model_all_of_links import VersionReadModelAllOfLinks

# TODO update the JSON string below
json = "{}"
# create an instance of VersionReadModelAllOfLinks from a JSON string
version_read_model_all_of_links_instance = VersionReadModelAllOfLinks.from_json(json)
# print the JSON string representation of the object
print(VersionReadModelAllOfLinks.to_json())

# convert the object into a dict
version_read_model_all_of_links_dict = version_read_model_all_of_links_instance.to_dict()
# create an instance of VersionReadModelAllOfLinks from a dict
version_read_model_all_of_links_from_dict = VersionReadModelAllOfLinks.from_dict(version_read_model_all_of_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


