# GroupCollectionModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**total** | **int** | The total amount of elements available in the collection. | 
**count** | **int** | Actual amount of elements in this response. | 
**links** | [**GroupCollectionModelAllOfLinks**](GroupCollectionModelAllOfLinks.md) |  | 
**embedded** | [**GroupCollectionModelAllOfEmbedded**](GroupCollectionModelAllOfEmbedded.md) |  | 

## Example

```python
from auto_slopp.openproject.openapi_client.models.group_collection_model import GroupCollectionModel

# TODO update the JSON string below
json = "{}"
# create an instance of GroupCollectionModel from a JSON string
group_collection_model_instance = GroupCollectionModel.from_json(json)
# print the JSON string representation of the object
print(GroupCollectionModel.to_json())

# convert the object into a dict
group_collection_model_dict = group_collection_model_instance.to_dict()
# create an instance of GroupCollectionModel from a dict
group_collection_model_from_dict = GroupCollectionModel.from_dict(group_collection_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


