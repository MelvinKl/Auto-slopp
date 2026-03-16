# ProgramModelAllOfLinks


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**update** | [**Link**](Link.md) | Form endpoint that aids in updating this program  # Conditions  **Permission**: edit workspace | [optional] 
**update_immediately** | [**Link**](Link.md) | Directly update this program  # Conditions  **Permission**: edit workspace | [optional] 
**delete** | [**Link**](Link.md) | Delete this program  # Conditions  **Permission**: admin | [optional] 
**favor** | [**Link**](Link.md) | Mark this program as favorited by the current user  # Conditions  Only present if the program is not yet favorited  Permission**: none but login is required | [optional] 
**disfavor** | [**Link**](Link.md) | Mark this program as not favorited by the current user  # Conditions Only present if the program is favorited by the current user  Permission**: none but login is required | [optional] 
**create_work_package** | [**Link**](Link.md) | Form endpoint that aids in preparing and creating a work package  # Conditions  **Permission**: add work packages | [optional] 
**create_work_package_immediately** | [**Link**](Link.md) | Directly creates a work package in the program  # Conditions  **Permission**: add work packages | [optional] 
**var_self** | [**Link**](Link.md) | This program  **Resource**: Program | 
**categories** | [**Link**](Link.md) | Categories available in this program  **Resource**: Collection | 
**types** | [**Link**](Link.md) | Types available in this program  **Resource**: Collection  # Conditions  **Permission**: view work packages or manage types | [optional] 
**versions** | [**Link**](Link.md) | Versions available in this program  **Resource**: Collection  # Conditions  **Permission**: view work packages or manage versions | [optional] 
**memberships** | [**Link**](Link.md) | Memberships in the  program  **Resource**: Collection  # Conditions  **Permission**: view members | [optional] 
**work_packages** | [**Link**](Link.md) | Work Packages of this program  **Resource**: Collection | [optional] 
**parent** | [**Link**](Link.md) | Parent of the program  **Resource**: Program  # Conditions  **Permission** edit workspace | [optional] 
**status** | [**Link**](Link.md) | Denotes the status of the program, so whether the program is on track, at risk or is having trouble.  **Resource**: ProjectStatus  # Conditions  **Permission** edit workspace | [optional] 
**storages** | [**List[ProgramModelAllOfLinksStorages]**](ProgramModelAllOfLinksStorages.md) |  | [optional] 
**project_storages** | [**Link**](Link.md) | The project storage collection of this program.  **Resource**: Collection  # Conditions  **Permission**: view_file_links | [optional] 
**ancestors** | [**List[ProgramModelAllOfLinksAncestors]**](ProgramModelAllOfLinksAncestors.md) |  | [optional] 

## Example

```python
from openproject_client.models.program_model_all_of_links import ProgramModelAllOfLinks

# TODO update the JSON string below
json = "{}"
# create an instance of ProgramModelAllOfLinks from a JSON string
program_model_all_of_links_instance = ProgramModelAllOfLinks.from_json(json)
# print the JSON string representation of the object
print(ProgramModelAllOfLinks.to_json())

# convert the object into a dict
program_model_all_of_links_dict = program_model_all_of_links_instance.to_dict()
# create an instance of ProgramModelAllOfLinks from a dict
program_model_all_of_links_from_dict = ProgramModelAllOfLinks.from_dict(program_model_all_of_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


