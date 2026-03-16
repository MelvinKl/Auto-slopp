# RelationCollectionModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**total** | **int** | The total amount of elements available in the collection. | 
**count** | **int** | Actual amount of elements in this response. | 
**links** | [**RelationCollectionModelAllOfLinks**](RelationCollectionModelAllOfLinks.md) |  | 
**embedded** | [**RelationCollectionModelAllOfEmbedded**](RelationCollectionModelAllOfEmbedded.md) |  | 

## Example

```python
from auto_slopp.openproject.openapi_client.models.relation_collection_model import RelationCollectionModel

# TODO update the JSON string below
json = "{}"
# create an instance of RelationCollectionModel from a JSON string
relation_collection_model_instance = RelationCollectionModel.from_json(json)
# print the JSON string representation of the object
print(RelationCollectionModel.to_json())

# convert the object into a dict
relation_collection_model_dict = relation_collection_model_instance.to_dict()
# create an instance of RelationCollectionModel from a dict
relation_collection_model_from_dict = RelationCollectionModel.from_dict(relation_collection_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


