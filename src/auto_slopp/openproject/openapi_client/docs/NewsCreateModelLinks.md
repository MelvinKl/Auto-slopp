# NewsCreateModelLinks


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**project** | [**Link**](Link.md) | The project the news is situated in  **Resource**: Project | 

## Example

```python
from auto_slopp.openproject.openapi_client.models.news_create_model_links import NewsCreateModelLinks

# TODO update the JSON string below
json = "{}"
# create an instance of NewsCreateModelLinks from a JSON string
news_create_model_links_instance = NewsCreateModelLinks.from_json(json)
# print the JSON string representation of the object
print(NewsCreateModelLinks.to_json())

# convert the object into a dict
news_create_model_links_dict = news_create_model_links_instance.to_dict()
# create an instance of NewsCreateModelLinks from a dict
news_create_model_links_from_dict = NewsCreateModelLinks.from_dict(news_create_model_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


