# WorkPackagePatchModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**subject** | **str** | Work package subject | [optional] 
**description** | [**Formattable**](Formattable.md) | The work package description | [optional] 
**schedule_manually** | **bool** | Uses manual scheduling mode when true (default). Uses automatic scheduling mode when false. Can be automatic only when predecessors or children are present. | [optional] 
**start_date** | **date** | Scheduled beginning of a work package | [optional] 
**due_date** | **date** | Scheduled end of a work package | [optional] 
**estimated_time** | **str** | Time a work package likely needs to be completed excluding its descendants | [optional] 
**duration** | **str** | The amount of time in hours the work package needs to be completed. This value must be bigger or equal to &#x60;P1D&#x60;, and any the value will get floored to the nearest day.  The duration has no effect, unless either a start date or a due date is set.  Not available for milestone type of work packages. | [optional] 
**ignore_non_working_days** | **bool** | When scheduling, whether or not to ignore the non working days being defined. A work package with the flag set to true will be allowed to be scheduled to a non working day. | [optional] 
**links** | [**WorkPackageWriteModelLinks**](WorkPackageWriteModelLinks.md) |  | [optional] 
**meta** | [**WorkPackageWriteModelMeta**](WorkPackageWriteModelMeta.md) |  | [optional] 
**lock_version** | **int** | The version of the item as used for optimistic locking | 

## Example

```python
from auto_slopp.openproject.openapi_client.models.work_package_patch_model import WorkPackagePatchModel

# TODO update the JSON string below
json = "{}"
# create an instance of WorkPackagePatchModel from a JSON string
work_package_patch_model_instance = WorkPackagePatchModel.from_json(json)
# print the JSON string representation of the object
print(WorkPackagePatchModel.to_json())

# convert the object into a dict
work_package_patch_model_dict = work_package_patch_model_instance.to_dict()
# create an instance of WorkPackagePatchModel from a dict
work_package_patch_model_from_dict = WorkPackagePatchModel.from_dict(work_package_patch_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


