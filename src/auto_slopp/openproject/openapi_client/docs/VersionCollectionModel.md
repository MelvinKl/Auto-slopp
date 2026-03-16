# VersionCollectionModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**total** | **int** | The total amount of elements available in the collection. | 
**count** | **int** | Actual amount of elements in this response. | 
**links** | [**VersionCollectionModelAllOfLinks**](VersionCollectionModelAllOfLinks.md) |  | 
**embedded** | [**VersionCollectionModelAllOfEmbedded**](VersionCollectionModelAllOfEmbedded.md) |  | 

## Example

```python
from auto_slopp.openproject.openapi_client.models.version_collection_model import VersionCollectionModel

# TODO update the JSON string below
json = "{}"
# create an instance of VersionCollectionModel from a JSON string
version_collection_model_instance = VersionCollectionModel.from_json(json)
# print the JSON string representation of the object
print(VersionCollectionModel.to_json())

# convert the object into a dict
version_collection_model_dict = version_collection_model_instance.to_dict()
# create an instance of VersionCollectionModel from a dict
version_collection_model_from_dict = VersionCollectionModel.from_dict(version_collection_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


