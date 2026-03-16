# WorkPackageModelAllOfLinks


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**add_comment** | [**Link**](Link.md) | Post comment to WP  # Conditions  **Permission**: add work package notes | [optional] [readonly] 
**add_relation** | [**Link**](Link.md) | Adds a relation to this work package.  # Conditions  **Permission**: manage wp relations | [optional] [readonly] 
**add_watcher** | [**Link**](Link.md) | Add any user to WP watchers  # Conditions  **Permission**: add watcher | [optional] [readonly] 
**custom_actions** | [**List[WorkPackageModelAllOfLinksCustomActions]**](WorkPackageModelAllOfLinksCustomActions.md) |  | [optional] [readonly] 
**preview_markup** | [**Link**](Link.md) | Post markup (in markdown) here to receive an HTML-rendered response | [optional] [readonly] 
**remove_watcher** | [**Link**](Link.md) | Remove any user from WP watchers  # Conditions  **Permission**: delete watcher | [optional] [readonly] 
**delete** | [**Link**](Link.md) | Delete this work package  # Conditions  **Permission**: delete_work_packages | [optional] [readonly] 
**log_time** | [**Link**](Link.md) | Create time entries on the work package  # Conditions  **Permission**: log_time or log_own_time | [optional] [readonly] 
**move** | [**Link**](Link.md) | Link to page for moving this work package  # Conditions  **Permission**: move_work_packages | [optional] [readonly] 
**copy** | [**Link**](Link.md) | Link to page for copying this work package  # Conditions  **Permission**: add_work_packages | [optional] [readonly] 
**unwatch** | [**Link**](Link.md) | Remove current user from WP watchers  # Conditions  logged in; watching | [optional] [readonly] 
**update** | [**Link**](Link.md) | Form endpoint that aids in preparing and performing edits on a work package  # Conditions  **Permission**: edit work package | [optional] [readonly] 
**update_immediately** | [**Link**](Link.md) | Directly perform edits on a work package  # Conditions  **Permission**: edit work package | [optional] [readonly] 
**watch** | [**Link**](Link.md) | Add current user to WP watchers  # Conditions  logged in; not watching | [optional] [readonly] 
**var_self** | [**Link**](Link.md) | This work package  **Resource**: WorkPackage | [readonly] 
**var_schema** | [**Link**](Link.md) | The schema of this work package  **Resource**: Schema | [readonly] 
**ancestors** | [**List[WorkPackageModelAllOfLinksAncestors]**](WorkPackageModelAllOfLinksAncestors.md) |  | [readonly] 
**attachments** | [**Link**](Link.md) | The files attached to this work package  **Resource**: Collection  # Conditions  - **Setting**: deactivate_work_package_attachments set to false in related workspace | [optional] 
**add_attachment** | [**Link**](Link.md) | Attach a file to the work package  # Conditions  - **Permission**: edit work package | [optional] [readonly] 
**prepare_attachment** | [**Link**](Link.md) | Attach a file to the work package  # Conditions  - **Setting**: direct uploads enabled | [optional] [readonly] 
**author** | [**Link**](Link.md) | The person that created the work package  **Resource**: User | [readonly] 
**assignee** | [**Link**](Link.md) | The person that is intended to work on the work package  **Resource**: User | [optional] 
**available_watchers** | [**Link**](Link.md) | All users that can be added to the work package as watchers.  **Resource**: User  # Conditions  **Permission** add work package watchers | [optional] [readonly] 
**budget** | [**Link**](Link.md) | The budget this work package is associated to  **Resource**: Budget  # Conditions  **Permission** view cost objects | [optional] 
**category** | [**Link**](Link.md) | The category of the work package  **Resource**: Category | [optional] 
**children** | [**List[WorkPackageModelAllOfLinksChildren]**](WorkPackageModelAllOfLinksChildren.md) |  | [optional] [readonly] 
**add_file_link** | [**Link**](Link.md) | Add a file link to the work package  # Conditions  **Permission**: manage_file_links | [optional] 
**file_links** | [**Link**](Link.md) | Gets the file link collection of this work package  # Conditions  **Permission**: view_file_links | [optional] 
**parent** | [**Link**](Link.md) | Parent work package  **Resource**: WorkPackage | [optional] 
**priority** | [**Link**](Link.md) | The priority of the work package  **Resource**: Priority | 
**project** | [**Link**](Link.md) | The workspace to which the work package belongs  **Resource**: Workspace | 
**project_phase** | [**Link**](Link.md) | The project phase to which the work package belongs  **Resource**: ProjectPhase | [optional] 
**project_phase_definition** | [**Link**](Link.md) | The definition of the project phase the work package belongs to  **Resource**: ProjectPhaseDefinition | [optional] 
**responsible** | [**Link**](Link.md) | The person that is responsible for the overall outcome  **Resource**: User | [optional] 
**relations** | [**Link**](Link.md) | Relations this work package is involved in  **Resource**: Relation  # Conditions  **Permission** view work packages | [optional] [readonly] 
**revisions** | [**Link**](Link.md) | Revisions that are referencing the work package  **Resource**: Revision  # Conditions  **Permission** view changesets | [optional] [readonly] 
**status** | [**Link**](Link.md) | The current status of the work package  **Resource**: Status | 
**time_entries** | [**Link**](Link.md) | All time entries logged on the work package. Please note that this is a link to an HTML resource for now and as such, the link is subject to change.  **Resource**: N/A  # Conditions  **Permission** view time entries | [optional] [readonly] 
**type** | [**Link**](Link.md) | The type of the work package  **Resource**: Type | 
**version** | [**Link**](Link.md) | The version associated to the work package  **Resource**: Version | [optional] 
**watchers** | [**Link**](Link.md) | All users that are currently watching this work package  **Resource**: Collection  # Conditions  **Permission** view work package watchers | [optional] [readonly] 

## Example

```python
from auto_slopp.openproject.openapi_client.models.work_package_model_all_of_links import WorkPackageModelAllOfLinks

# TODO update the JSON string below
json = "{}"
# create an instance of WorkPackageModelAllOfLinks from a JSON string
work_package_model_all_of_links_instance = WorkPackageModelAllOfLinks.from_json(json)
# print the JSON string representation of the object
print(WorkPackageModelAllOfLinks.to_json())

# convert the object into a dict
work_package_model_all_of_links_dict = work_package_model_all_of_links_instance.to_dict()
# create an instance of WorkPackageModelAllOfLinks from a dict
work_package_model_all_of_links_from_dict = WorkPackageModelAllOfLinks.from_dict(work_package_model_all_of_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


