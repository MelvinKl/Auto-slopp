# OffsetPaginatedCollectionModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**total** | **int** | The total amount of elements available in the collection. | 
**count** | **int** | Actual amount of elements in this response. | 
**links** | [**OffsetPaginatedCollectionLinks**](OffsetPaginatedCollectionLinks.md) |  | 
**page_size** | **int** | The amount of elements per page. If not set by the request this value defaults to the server&#39;s system settings. | 
**offset** | **int** | The page offset indicating on which page the element collection starts. | 

## Example

```python
from auto_slopp.openproject.openapi_client.models.offset_paginated_collection_model import OffsetPaginatedCollectionModel

# TODO update the JSON string below
json = "{}"
# create an instance of OffsetPaginatedCollectionModel from a JSON string
offset_paginated_collection_model_instance = OffsetPaginatedCollectionModel.from_json(json)
# print the JSON string representation of the object
print(OffsetPaginatedCollectionModel.to_json())

# convert the object into a dict
offset_paginated_collection_model_dict = offset_paginated_collection_model_instance.to_dict()
# create an instance of OffsetPaginatedCollectionModel from a dict
offset_paginated_collection_model_from_dict = OffsetPaginatedCollectionModel.from_dict(offset_paginated_collection_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


