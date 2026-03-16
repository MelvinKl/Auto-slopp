# NewsModelLinks


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_self** | [**Link**](Link.md) | This news  **Resource**: News | [readonly] 
**project** | [**Link**](Link.md) | The workspace the news is situated in  **Resource**: workspace | 
**author** | [**Link**](Link.md) | The user having created the news  **Resource**: User | [readonly] 
**update_immediately** | [**Link**](Link.md) | Directly perform edits on the news  **Permission** manage news | [optional] 
**delete** | [**Link**](Link.md) | Delete the news  **Permission** manage news | [optional] 

## Example

```python
from auto_slopp.openproject.openapi_client.models.news_model_links import NewsModelLinks

# TODO update the JSON string below
json = "{}"
# create an instance of NewsModelLinks from a JSON string
news_model_links_instance = NewsModelLinks.from_json(json)
# print the JSON string representation of the object
print(NewsModelLinks.to_json())

# convert the object into a dict
news_model_links_dict = news_model_links_instance.to_dict()
# create an instance of NewsModelLinks from a dict
news_model_links_from_dict = NewsModelLinks.from_dict(news_model_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


