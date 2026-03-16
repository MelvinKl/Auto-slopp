# WorkPackageModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** | Work package id | [optional] [readonly] 
**lock_version** | **int** | The version of the item as used for optimistic locking | [optional] [readonly] 
**subject** | **str** | Work package subject | 
**type** | **str** |  | [optional] [readonly] 
**description** | [**Formattable**](Formattable.md) | The work package description | [optional] 
**schedule_manually** | **bool** | Uses manual scheduling mode when true (default). Uses automatic scheduling mode when false. Can be automatic only when predecessors or children are present. | [optional] 
**readonly** | **bool** | If true, the work package is in a readonly status so with the exception of the status, no other property can be altered. | [optional] 
**start_date** | **date** | Scheduled beginning of a work package | [optional] 
**due_date** | **date** | Scheduled end of a work package | [optional] 
**var_date** | **date** | Date on which a milestone is achieved | [optional] 
**derived_start_date** | **date** | Similar to start date but is not set by a client but rather deduced by the work packages&#39; descendants. If manual scheduleManually is active, the two dates can deviate. | [optional] [readonly] 
**derived_due_date** | **date** | Similar to due date but is not set by a client but rather deduced by the work packages&#39; descendants. If manual scheduleManually is active, the two dates can deviate. | [optional] [readonly] 
**duration** | **str** | **(NOT IMPLEMENTED)** The amount of time in hours the work package needs to be completed. Not available for milestone type of work packages. | [optional] [readonly] 
**estimated_time** | **str** | Time a work package likely needs to be completed excluding its descendants | [optional] 
**derived_estimated_time** | **str** | Time a work package likely needs to be completed including its descendants | [optional] [readonly] 
**ignore_non_working_days** | **bool** | **(NOT IMPLEMENTED)** When scheduling, whether or not to ignore the non working days being defined. A work package with the flag set to true will be allowed to be scheduled to a non working day. | [optional] [readonly] 
**spent_time** | **str** | The time booked for this work package by users working on it  # Conditions  **Permission** view time entries | [optional] [readonly] 
**percentage_done** | **int** | Amount of total completion for a work package | [optional] 
**derived_percentage_done** | **int** | Amount of total completion for a work package derived from itself and its descendant work packages | [optional] [readonly] 
**created_at** | **datetime** | Time of creation. Can be writable by admins with the &#x60;apiv3_write_readonly_attributes&#x60; setting enabled. | [optional] [readonly] 
**updated_at** | **datetime** | Time of the most recent change to the work package. | [optional] [readonly] 
**links** | [**WorkPackageModelAllOfLinks**](WorkPackageModelAllOfLinks.md) |  | 

## Example

```python
from auto_slopp.openproject.openapi_client.models.work_package_model import WorkPackageModel

# TODO update the JSON string below
json = "{}"
# create an instance of WorkPackageModel from a JSON string
work_package_model_instance = WorkPackageModel.from_json(json)
# print the JSON string representation of the object
print(WorkPackageModel.to_json())

# convert the object into a dict
work_package_model_dict = work_package_model_instance.to_dict()
# create an instance of WorkPackageModel from a dict
work_package_model_from_dict = WorkPackageModel.from_dict(work_package_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


