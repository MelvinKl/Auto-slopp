# WorkPackageSchemaModel

A schema for a work package. This schema defines the attributes of a work package.  TODO: Incomplete, needs to be updated with the real behaviour of schemas (when does which attribute appear?).

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | [optional] 
**dependencies** | **List[str]** | TBD | [optional] 
**attribute_groups** | **List[object]** | TBD (WorkPackageFormAttributeGroup) | [optional] 
**lock_version** | [**SchemaPropertyModel**](SchemaPropertyModel.md) |  | [optional] 
**id** | [**SchemaPropertyModel**](SchemaPropertyModel.md) |  | [optional] 
**subject** | [**SchemaPropertyModel**](SchemaPropertyModel.md) |  | [optional] 
**description** | [**SchemaPropertyModel**](SchemaPropertyModel.md) |  | [optional] 
**duration** | [**SchemaPropertyModel**](SchemaPropertyModel.md) |  | [optional] 
**schedule_manually** | [**SchemaPropertyModel**](SchemaPropertyModel.md) |  | [optional] 
**ignore_non_working_days** | [**SchemaPropertyModel**](SchemaPropertyModel.md) |  | [optional] 
**start_date** | [**SchemaPropertyModel**](SchemaPropertyModel.md) |  | [optional] 
**due_date** | [**SchemaPropertyModel**](SchemaPropertyModel.md) |  | [optional] 
**derived_start_date** | [**SchemaPropertyModel**](SchemaPropertyModel.md) |  | [optional] 
**derived_due_date** | [**SchemaPropertyModel**](SchemaPropertyModel.md) |  | [optional] 
**estimated_time** | [**SchemaPropertyModel**](SchemaPropertyModel.md) |  | [optional] 
**derived_estimated_time** | [**SchemaPropertyModel**](SchemaPropertyModel.md) |  | [optional] 
**remaining_time** | [**SchemaPropertyModel**](SchemaPropertyModel.md) |  | [optional] 
**derived_remaining_time** | [**SchemaPropertyModel**](SchemaPropertyModel.md) |  | [optional] 
**percentage_done** | [**SchemaPropertyModel**](SchemaPropertyModel.md) |  | [optional] 
**derived_percentage_done** | [**SchemaPropertyModel**](SchemaPropertyModel.md) |  | [optional] 
**readonly** | [**SchemaPropertyModel**](SchemaPropertyModel.md) |  | [optional] 
**created_at** | [**SchemaPropertyModel**](SchemaPropertyModel.md) |  | [optional] 
**updated_at** | [**SchemaPropertyModel**](SchemaPropertyModel.md) |  | [optional] 
**author** | [**SchemaPropertyModel**](SchemaPropertyModel.md) |  | [optional] 
**project** | [**SchemaPropertyModel**](SchemaPropertyModel.md) |  | [optional] 
**project_phase** | [**SchemaPropertyModel**](SchemaPropertyModel.md) |  | [optional] 
**project_phase_definition** | [**SchemaPropertyModel**](SchemaPropertyModel.md) |  | [optional] 
**parent** | [**SchemaPropertyModel**](SchemaPropertyModel.md) |  | [optional] 
**assignee** | [**SchemaPropertyModel**](SchemaPropertyModel.md) |  | [optional] 
**responsible** | [**SchemaPropertyModel**](SchemaPropertyModel.md) |  | [optional] 
**type** | [**SchemaPropertyModel**](SchemaPropertyModel.md) |  | [optional] 
**status** | [**SchemaPropertyModel**](SchemaPropertyModel.md) |  | [optional] 
**category** | [**SchemaPropertyModel**](SchemaPropertyModel.md) |  | [optional] 
**version** | [**SchemaPropertyModel**](SchemaPropertyModel.md) |  | [optional] 
**priority** | [**SchemaPropertyModel**](SchemaPropertyModel.md) |  | [optional] 
**links** | [**WorkPackageSchemaModelLinks**](WorkPackageSchemaModelLinks.md) |  | [optional] 

## Example

```python
from openproject_client.models.work_package_schema_model import WorkPackageSchemaModel

# TODO update the JSON string below
json = "{}"
# create an instance of WorkPackageSchemaModel from a JSON string
work_package_schema_model_instance = WorkPackageSchemaModel.from_json(json)
# print the JSON string representation of the object
print(WorkPackageSchemaModel.to_json())

# convert the object into a dict
work_package_schema_model_dict = work_package_schema_model_instance.to_dict()
# create an instance of WorkPackageSchemaModel from a dict
work_package_schema_model_from_dict = WorkPackageSchemaModel.from_dict(work_package_schema_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


