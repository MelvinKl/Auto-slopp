# AvailableAssigneesModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**total** | **int** | The total amount of elements available in the collection. | 
**count** | **int** | Actual amount of elements in this response. | 
**links** | [**AvailableAssigneesModelAllOfLinks**](AvailableAssigneesModelAllOfLinks.md) |  | 
**embedded** | [**AvailableAssigneesModelAllOfEmbedded**](AvailableAssigneesModelAllOfEmbedded.md) |  | 

## Example

```python
from auto_slopp.openproject.openapi_client.models.available_assignees_model import AvailableAssigneesModel

# TODO update the JSON string below
json = "{}"
# create an instance of AvailableAssigneesModel from a JSON string
available_assignees_model_instance = AvailableAssigneesModel.from_json(json)
# print the JSON string representation of the object
print(AvailableAssigneesModel.to_json())

# convert the object into a dict
available_assignees_model_dict = available_assignees_model_instance.to_dict()
# create an instance of AvailableAssigneesModel from a dict
available_assignees_model_from_dict = AvailableAssigneesModel.from_dict(available_assignees_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


