# ProjectStorageModelLinks


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_self** | [**Link**](Link.md) | This project storage.  **Resource**: ProjectStorage | 
**creator** | [**Link**](Link.md) | The user who created the project storage.  **Resource**: User | 
**storage** | [**Link**](Link.md) | The storage resource, that is linked to a project with this project storage.  **Resource**: Storage | 
**project** | [**Link**](Link.md) | The project resource, that is linked to a storage with this project storage.  **Resource**: Project | 
**project_folder** | [**Link**](Link.md) | The directory on the storage that is used as a project folder.  **Resource**: StorageFile  # Conditions  Only provided, if the &#x60;projectFolderMode&#x60; is &#x60;manual&#x60; or &#x60;automatic&#x60;. | [optional] 
**open** | [**Link**](Link.md) | A link to OpenProject strorage.  # Conditions  If the storage has not been configured(oauth client is missing, for instance), then the link is null. | [optional] 
**open_with_connection_ensured** | [**Link**](Link.md) | A link to OpenProject storage with making sure user has access to it.  **Deprecated:** Use &#x60;open&#x60; instead, which returns a link that will ensure the user&#39;s connection to the storage as well, but properly works for all kinds of storage configurations. | [optional] 

## Example

```python
from auto_slopp.openproject.openapi_client.models.project_storage_model_links import ProjectStorageModelLinks

# TODO update the JSON string below
json = "{}"
# create an instance of ProjectStorageModelLinks from a JSON string
project_storage_model_links_instance = ProjectStorageModelLinks.from_json(json)
# print the JSON string representation of the object
print(ProjectStorageModelLinks.to_json())

# convert the object into a dict
project_storage_model_links_dict = project_storage_model_links_instance.to_dict()
# create an instance of ProjectStorageModelLinks from a dict
project_storage_model_links_from_dict = ProjectStorageModelLinks.from_dict(project_storage_model_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


