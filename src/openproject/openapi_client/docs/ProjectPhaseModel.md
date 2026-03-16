# ProjectPhaseModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**id** | **int** | The project phase&#39;s id | 
**name** | **str** |  | 
**active** | **bool** |  | 
**created_at** | **datetime** | Time of creation | 
**updated_at** | **datetime** | Time of the most recent change to the project phase | 
**links** | [**ProjectPhaseModelLinks**](ProjectPhaseModelLinks.md) |  | [optional] 

## Example

```python
from openproject_client.models.project_phase_model import ProjectPhaseModel

# TODO update the JSON string below
json = "{}"
# create an instance of ProjectPhaseModel from a JSON string
project_phase_model_instance = ProjectPhaseModel.from_json(json)
# print the JSON string representation of the object
print(ProjectPhaseModel.to_json())

# convert the object into a dict
project_phase_model_dict = project_phase_model_instance.to_dict()
# create an instance of ProjectPhaseModel from a dict
project_phase_model_from_dict = ProjectPhaseModel.from_dict(project_phase_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


