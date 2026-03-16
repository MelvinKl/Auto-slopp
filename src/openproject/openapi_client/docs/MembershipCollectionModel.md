# MembershipCollectionModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**total** | **int** | The total amount of elements available in the collection. | 
**count** | **int** | Actual amount of elements in this response. | 
**links** | [**PaginatedCollectionModelAllOfLinks**](PaginatedCollectionModelAllOfLinks.md) |  | 
**page_size** | **int** | Amount of elements that a response will hold. | 
**offset** | **int** | The page number that is requested from paginated collection. | 
**embedded** | [**MembershipCollectionModelAllOfEmbedded**](MembershipCollectionModelAllOfEmbedded.md) |  | 

## Example

```python
from openproject_client.models.membership_collection_model import MembershipCollectionModel

# TODO update the JSON string below
json = "{}"
# create an instance of MembershipCollectionModel from a JSON string
membership_collection_model_instance = MembershipCollectionModel.from_json(json)
# print the JSON string representation of the object
print(MembershipCollectionModel.to_json())

# convert the object into a dict
membership_collection_model_dict = membership_collection_model_instance.to_dict()
# create an instance of MembershipCollectionModel from a dict
membership_collection_model_from_dict = MembershipCollectionModel.from_dict(membership_collection_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


