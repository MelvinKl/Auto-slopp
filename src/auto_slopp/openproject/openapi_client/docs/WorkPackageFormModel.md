# WorkPackageFormModel

The work package creation form. This object is returned, whenever a work package form endpoint is called. It contains an allowed payload definition, the full schema and any validation errors on the current request body.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | [optional] 
**embedded** | [**WorkPackageFormModelEmbedded**](WorkPackageFormModelEmbedded.md) |  | [optional] 
**links** | [**WorkPackageFormModelLinks**](WorkPackageFormModelLinks.md) |  | [optional] 

## Example

```python
from auto_slopp.openproject.openapi_client.models.work_package_form_model import WorkPackageFormModel

# TODO update the JSON string below
json = "{}"
# create an instance of WorkPackageFormModel from a JSON string
work_package_form_model_instance = WorkPackageFormModel.from_json(json)
# print the JSON string representation of the object
print(WorkPackageFormModel.to_json())

# convert the object into a dict
work_package_form_model_dict = work_package_form_model_instance.to_dict()
# create an instance of WorkPackageFormModel from a dict
work_package_form_model_from_dict = WorkPackageFormModel.from_dict(work_package_form_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


