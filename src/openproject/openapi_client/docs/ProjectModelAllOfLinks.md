# ProjectModelAllOfLinks


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**update** | [**Link**](Link.md) | Form endpoint that aids in updating this project  # Conditions  **Permission**: edit workspace | [optional] 
**update_immediately** | [**Link**](Link.md) | Directly update this project  # Conditions  **Permission**: edit workspace | [optional] 
**delete** | [**Link**](Link.md) | Delete this project  # Conditions  **Permission**: admin | [optional] 
**favor** | [**Link**](Link.md) | Mark this project as favorited by the current user  # Conditions  Only present if the project is not yet favorited  Permission**: none but login is required | [optional] 
**disfavor** | [**Link**](Link.md) | Mark this project as not favorited by the current user  # Conditions Only present if the project is favorited by the current user  Permission**: none but login is required | [optional] 
**create_work_package** | [**Link**](Link.md) | Form endpoint that aids in preparing and creating a work package  # Conditions  **Permission**: add work packages | [optional] 
**create_work_package_immediately** | [**Link**](Link.md) | Directly creates a work package in the project  # Conditions  **Permission**: add work packages | [optional] 
**var_self** | [**Link**](Link.md) | This project  **Resource**: Project | 
**categories** | [**Link**](Link.md) | Categories available in this project  **Resource**: Collection | 
**types** | [**Link**](Link.md) | Types available in this project  **Resource**: Collection  # Conditions  **Permission**: view work packages or manage types | [optional] 
**versions** | [**Link**](Link.md) | Versions available in this project  **Resource**: Collection  # Conditions  **Permission**: view work packages or manage versions | [optional] 
**memberships** | [**Link**](Link.md) | Memberships in the project  **Resource**: Collection  # Conditions  **Permission**: view members | [optional] 
**work_packages** | [**Link**](Link.md) | Work Packages of this project  **Resource**: Collection | [optional] 
**parent** | [**Link**](Link.md) | Parent of the project  **Resource**: Workspace  # Conditions  **Permission** edit workspace | [optional] 
**status** | [**Link**](Link.md) | Denotes the status of the project, so whether the project is on track, at risk or is having trouble.  **Resource**: ProjectStatus  # Conditions  **Permission** edit workspace | [optional] 
**storages** | [**List[ProjectModelAllOfLinksStorages]**](ProjectModelAllOfLinksStorages.md) |  | [optional] 
**project_storages** | [**Link**](Link.md) | The project storage collection of this project.  **Resource**: Collection  # Conditions  **Permission**: view_file_links | [optional] 
**ancestors** | [**List[ProjectModelAllOfLinksAncestors]**](ProjectModelAllOfLinksAncestors.md) |  | [optional] 

## Example

```python
from openproject_client.models.project_model_all_of_links import ProjectModelAllOfLinks

# TODO update the JSON string below
json = "{}"
# create an instance of ProjectModelAllOfLinks from a JSON string
project_model_all_of_links_instance = ProjectModelAllOfLinks.from_json(json)
# print the JSON string representation of the object
print(ProjectModelAllOfLinks.to_json())

# convert the object into a dict
project_model_all_of_links_dict = project_model_all_of_links_instance.to_dict()
# create an instance of ProjectModelAllOfLinks from a dict
project_model_all_of_links_from_dict = ProjectModelAllOfLinks.from_dict(project_model_all_of_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


