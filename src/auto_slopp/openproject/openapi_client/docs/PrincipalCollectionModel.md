# PrincipalCollectionModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**total** | **int** | The total amount of elements available in the collection. | 
**count** | **int** | Actual amount of elements in this response. | 
**links** | [**OffsetPaginatedCollectionLinks**](OffsetPaginatedCollectionLinks.md) |  | 
**page_size** | **int** | The amount of elements per page. If not set by the request this value defaults to the server&#39;s system settings. | 
**offset** | **int** | The page offset indicating on which page the element collection starts. | 
**embedded** | [**PrincipalCollectionModelAllOfEmbedded**](PrincipalCollectionModelAllOfEmbedded.md) |  | 

## Example

```python
from auto_slopp.openproject.openapi_client.models.principal_collection_model import PrincipalCollectionModel

# TODO update the JSON string below
json = "{}"
# create an instance of PrincipalCollectionModel from a JSON string
principal_collection_model_instance = PrincipalCollectionModel.from_json(json)
# print the JSON string representation of the object
print(PrincipalCollectionModel.to_json())

# convert the object into a dict
principal_collection_model_dict = principal_collection_model_instance.to_dict()
# create an instance of PrincipalCollectionModel from a dict
principal_collection_model_from_dict = PrincipalCollectionModel.from_dict(principal_collection_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


