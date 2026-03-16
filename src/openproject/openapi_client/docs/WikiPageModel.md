# WikiPageModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** | Identifier of this wiki page | [optional] [readonly] 
**title** | **str** | The wiki page&#39;s title | 
**links** | [**WikiPageModelLinks**](WikiPageModelLinks.md) |  | [optional] 

## Example

```python
from openproject_client.models.wiki_page_model import WikiPageModel

# TODO update the JSON string below
json = "{}"
# create an instance of WikiPageModel from a JSON string
wiki_page_model_instance = WikiPageModel.from_json(json)
# print the JSON string representation of the object
print(WikiPageModel.to_json())

# convert the object into a dict
wiki_page_model_dict = wiki_page_model_instance.to_dict()
# create an instance of WikiPageModel from a dict
wiki_page_model_from_dict = WikiPageModel.from_dict(wiki_page_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


