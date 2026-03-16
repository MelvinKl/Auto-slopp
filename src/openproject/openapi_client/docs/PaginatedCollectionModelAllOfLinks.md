# PaginatedCollectionModelAllOfLinks


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**jump_to** | [**Link**](Link.md) | Templated link to another page offset.  **Resource**: Collection | 
**change_size** | [**Link**](Link.md) | Templated link for another page size.  **Resource**: Collection | 

## Example

```python
from openproject_client.models.paginated_collection_model_all_of_links import PaginatedCollectionModelAllOfLinks

# TODO update the JSON string below
json = "{}"
# create an instance of PaginatedCollectionModelAllOfLinks from a JSON string
paginated_collection_model_all_of_links_instance = PaginatedCollectionModelAllOfLinks.from_json(json)
# print the JSON string representation of the object
print(PaginatedCollectionModelAllOfLinks.to_json())

# convert the object into a dict
paginated_collection_model_all_of_links_dict = paginated_collection_model_all_of_links_instance.to_dict()
# create an instance of PaginatedCollectionModelAllOfLinks from a dict
paginated_collection_model_all_of_links_from_dict = PaginatedCollectionModelAllOfLinks.from_dict(paginated_collection_model_all_of_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


