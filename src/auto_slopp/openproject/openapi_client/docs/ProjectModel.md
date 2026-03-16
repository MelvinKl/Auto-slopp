# ProjectModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | [optional] 
**id** | **int** | Projects&#39; id | [optional] 
**identifier** | **str** |  | [optional] 
**name** | **str** |  | [optional] 
**active** | **bool** | Indicates whether the project is currently active or already archived | [optional] 
**favorited** | **bool** | Indicates whether the project is favorited by the current user | [optional] 
**status_explanation** | [**Formattable**](Formattable.md) | A text detailing and explaining why the project has the reported status | [optional] 
**public** | **bool** | Indicates whether the project is accessible for everybody | [optional] 
**description** | [**Formattable**](Formattable.md) |  | [optional] 
**created_at** | **datetime** | Time of creation. Can be writable by admins with the &#x60;apiv3_write_readonly_attributes&#x60; setting enabled. | [optional] 
**updated_at** | **datetime** | Time of the most recent change to the project | [optional] 
**links** | [**ProjectModelAllOfLinks**](ProjectModelAllOfLinks.md) |  | [optional] 

## Example

```python
from auto_slopp.openproject.openapi_client.models.project_model import ProjectModel

# TODO update the JSON string below
json = "{}"
# create an instance of ProjectModel from a JSON string
project_model_instance = ProjectModel.from_json(json)
# print the JSON string representation of the object
print(ProjectModel.to_json())

# convert the object into a dict
project_model_dict = project_model_instance.to_dict()
# create an instance of ProjectModel from a dict
project_model_from_dict = ProjectModel.from_dict(project_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


