# HierarchyItemCollectionModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**total** | **int** | The total amount of elements available in the collection. | 
**count** | **int** | Actual amount of elements in this response. | 
**links** | [**HierarchyItemCollectionModelAllOfLinks**](HierarchyItemCollectionModelAllOfLinks.md) |  | 
**embedded** | [**HierarchyItemCollectionModelAllOfEmbedded**](HierarchyItemCollectionModelAllOfEmbedded.md) |  | 

## Example

```python
from auto_slopp.openproject.openapi_client.models.hierarchy_item_collection_model import HierarchyItemCollectionModel

# TODO update the JSON string below
json = "{}"
# create an instance of HierarchyItemCollectionModel from a JSON string
hierarchy_item_collection_model_instance = HierarchyItemCollectionModel.from_json(json)
# print the JSON string representation of the object
print(HierarchyItemCollectionModel.to_json())

# convert the object into a dict
hierarchy_item_collection_model_dict = hierarchy_item_collection_model_instance.to_dict()
# create an instance of HierarchyItemCollectionModel from a dict
hierarchy_item_collection_model_from_dict = HierarchyItemCollectionModel.from_dict(hierarchy_item_collection_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


