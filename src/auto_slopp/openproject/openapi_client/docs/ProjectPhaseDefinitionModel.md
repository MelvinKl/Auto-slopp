# ProjectPhaseDefinitionModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**id** | **int** | The project phase definition&#39;s id | 
**name** | **str** |  | 
**start_gate** | **bool** |  | 
**start_gate_name** | **str** |  | 
**finish_gate** | **bool** |  | 
**finish_gate_name** | **str** |  | 
**created_at** | **datetime** | Time of creation | 
**updated_at** | **datetime** | Time of the most recent change to the project phase definition | 
**links** | [**ProjectPhaseDefinitionModelLinks**](ProjectPhaseDefinitionModelLinks.md) |  | [optional] 

## Example

```python
from auto_slopp.openproject.openapi_client.models.project_phase_definition_model import ProjectPhaseDefinitionModel

# TODO update the JSON string below
json = "{}"
# create an instance of ProjectPhaseDefinitionModel from a JSON string
project_phase_definition_model_instance = ProjectPhaseDefinitionModel.from_json(json)
# print the JSON string representation of the object
print(ProjectPhaseDefinitionModel.to_json())

# convert the object into a dict
project_phase_definition_model_dict = project_phase_definition_model_instance.to_dict()
# create an instance of ProjectPhaseDefinitionModel from a dict
project_phase_definition_model_from_dict = ProjectPhaseDefinitionModel.from_dict(project_phase_definition_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


