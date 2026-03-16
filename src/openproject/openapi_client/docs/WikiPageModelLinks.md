# WikiPageModelLinks


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**add_attachment** | [**Link**](Link.md) | Attach a file to the wiki page  # Conditions  **Permission**: edit wiki page | [optional] [readonly] 

## Example

```python
from openproject_client.models.wiki_page_model_links import WikiPageModelLinks

# TODO update the JSON string below
json = "{}"
# create an instance of WikiPageModelLinks from a JSON string
wiki_page_model_links_instance = WikiPageModelLinks.from_json(json)
# print the JSON string representation of the object
print(WikiPageModelLinks.to_json())

# convert the object into a dict
wiki_page_model_links_dict = wiki_page_model_links_instance.to_dict()
# create an instance of WikiPageModelLinks from a dict
wiki_page_model_links_from_dict = WikiPageModelLinks.from_dict(wiki_page_model_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


