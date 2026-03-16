# OffsetPaginatedCollectionLinks


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_self** | [**Link**](Link.md) | This collection resource.  **Resource**: Collection | 
**jump_to** | [**Link**](Link.md) | A templated link to jump to a given offset. | 
**change_size** | [**Link**](Link.md) | A templated link to change the current page size. | 
**previous_by_offset** | [**Link**](Link.md) | A link to the previous page of the collection.  # Conditions - The collection is not on the first page. | [optional] 
**next_by_offset** | [**Link**](Link.md) | A link to the next page of the collection.  # Conditions - The collection is not on the last page. | [optional] 

## Example

```python
from openproject_client.models.offset_paginated_collection_links import OffsetPaginatedCollectionLinks

# TODO update the JSON string below
json = "{}"
# create an instance of OffsetPaginatedCollectionLinks from a JSON string
offset_paginated_collection_links_instance = OffsetPaginatedCollectionLinks.from_json(json)
# print the JSON string representation of the object
print(OffsetPaginatedCollectionLinks.to_json())

# convert the object into a dict
offset_paginated_collection_links_dict = offset_paginated_collection_links_instance.to_dict()
# create an instance of OffsetPaginatedCollectionLinks from a dict
offset_paginated_collection_links_from_dict = OffsetPaginatedCollectionLinks.from_dict(offset_paginated_collection_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


