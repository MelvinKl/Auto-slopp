# ProjectCollectionModelAllOfLinks


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_self** | [**Link**](Link.md) | This collection resource.  **Resource**: Collection | 
**jump_to** | [**Link**](Link.md) | A templated link to jump to a given offset. | 
**change_size** | [**Link**](Link.md) | A templated link to change the current page size. | 
**previous_by_offset** | [**Link**](Link.md) | A link to the previous page of the collection.  # Conditions - The collection is not on the first page. | [optional] 
**next_by_offset** | [**Link**](Link.md) | A link to the next page of the collection.  # Conditions - The collection is not on the last page. | [optional] 
**representations** | [**List[Link]**](Link.md) |  | [optional] 

## Example

```python
from openproject_client.models.project_collection_model_all_of_links import ProjectCollectionModelAllOfLinks

# TODO update the JSON string below
json = "{}"
# create an instance of ProjectCollectionModelAllOfLinks from a JSON string
project_collection_model_all_of_links_instance = ProjectCollectionModelAllOfLinks.from_json(json)
# print the JSON string representation of the object
print(ProjectCollectionModelAllOfLinks.to_json())

# convert the object into a dict
project_collection_model_all_of_links_dict = project_collection_model_all_of_links_instance.to_dict()
# create an instance of ProjectCollectionModelAllOfLinks from a dict
project_collection_model_all_of_links_from_dict = ProjectCollectionModelAllOfLinks.from_dict(project_collection_model_all_of_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


