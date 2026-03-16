# ProgramCollectionModelAllOfLinks


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
from auto_slopp.openproject.openapi_client.models.program_collection_model_all_of_links import ProgramCollectionModelAllOfLinks

# TODO update the JSON string below
json = "{}"
# create an instance of ProgramCollectionModelAllOfLinks from a JSON string
program_collection_model_all_of_links_instance = ProgramCollectionModelAllOfLinks.from_json(json)
# print the JSON string representation of the object
print(ProgramCollectionModelAllOfLinks.to_json())

# convert the object into a dict
program_collection_model_all_of_links_dict = program_collection_model_all_of_links_instance.to_dict()
# create an instance of ProgramCollectionModelAllOfLinks from a dict
program_collection_model_all_of_links_from_dict = ProgramCollectionModelAllOfLinks.from_dict(program_collection_model_all_of_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


