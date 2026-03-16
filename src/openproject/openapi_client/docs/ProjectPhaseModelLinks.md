# ProjectPhaseModelLinks


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_self** | [**Link**](Link.md) | This project phase.  **Resource**: ProjectPhase | 
**definition** | [**Link**](Link.md) | The definition this phase relies on.  **Resource**: ProjectPhaseDefinition | 
**project** | [**Link**](Link.md) | The project resource, that is the container of this phase.  **Resource**: Project | 

## Example

```python
from openproject_client.models.project_phase_model_links import ProjectPhaseModelLinks

# TODO update the JSON string below
json = "{}"
# create an instance of ProjectPhaseModelLinks from a JSON string
project_phase_model_links_instance = ProjectPhaseModelLinks.from_json(json)
# print the JSON string representation of the object
print(ProjectPhaseModelLinks.to_json())

# convert the object into a dict
project_phase_model_links_dict = project_phase_model_links_instance.to_dict()
# create an instance of ProjectPhaseModelLinks from a dict
project_phase_model_links_from_dict = ProjectPhaseModelLinks.from_dict(project_phase_model_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


