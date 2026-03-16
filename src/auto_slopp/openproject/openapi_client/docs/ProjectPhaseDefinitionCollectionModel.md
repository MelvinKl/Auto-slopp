# ProjectPhaseDefinitionCollectionModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**total** | **int** | The total amount of elements available in the collection. | 
**count** | **int** | Actual amount of elements in this response. | 
**links** | [**ProjectPhaseDefinitionCollectionModelAllOfLinks**](ProjectPhaseDefinitionCollectionModelAllOfLinks.md) |  | 
**page_size** | **int** | The amount of elements per page. If not set by the request this value defaults to the server&#39;s system settings. | 
**offset** | **int** | The page offset indicating on which page the element collection starts. | 
**embedded** | [**ProjectPhaseDefinitionCollectionModelAllOfEmbedded**](ProjectPhaseDefinitionCollectionModelAllOfEmbedded.md) |  | 

## Example

```python
from auto_slopp.openproject.openapi_client.models.project_phase_definition_collection_model import ProjectPhaseDefinitionCollectionModel

# TODO update the JSON string below
json = "{}"
# create an instance of ProjectPhaseDefinitionCollectionModel from a JSON string
project_phase_definition_collection_model_instance = ProjectPhaseDefinitionCollectionModel.from_json(json)
# print the JSON string representation of the object
print(ProjectPhaseDefinitionCollectionModel.to_json())

# convert the object into a dict
project_phase_definition_collection_model_dict = project_phase_definition_collection_model_instance.to_dict()
# create an instance of ProjectPhaseDefinitionCollectionModel from a dict
project_phase_definition_collection_model_from_dict = ProjectPhaseDefinitionCollectionModel.from_dict(project_phase_definition_collection_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


