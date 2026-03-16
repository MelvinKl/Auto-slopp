# ProgramCollectionModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**total** | **int** | The total amount of elements available in the collection. | 
**count** | **int** | Actual amount of elements in this response. | 
**links** | [**ProgramCollectionModelAllOfLinks**](ProgramCollectionModelAllOfLinks.md) |  | 
**page_size** | **int** | The amount of elements per page. If not set by the request this value defaults to the server&#39;s system settings. | 
**offset** | **int** | The page offset indicating on which page the element collection starts. | 
**embedded** | [**ProgramCollectionModelAllOfEmbedded**](ProgramCollectionModelAllOfEmbedded.md) |  | 

## Example

```python
from auto_slopp.openproject.openapi_client.models.program_collection_model import ProgramCollectionModel

# TODO update the JSON string below
json = "{}"
# create an instance of ProgramCollectionModel from a JSON string
program_collection_model_instance = ProgramCollectionModel.from_json(json)
# print the JSON string representation of the object
print(ProgramCollectionModel.to_json())

# convert the object into a dict
program_collection_model_dict = program_collection_model_instance.to_dict()
# create an instance of ProgramCollectionModel from a dict
program_collection_model_from_dict = ProgramCollectionModel.from_dict(program_collection_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


