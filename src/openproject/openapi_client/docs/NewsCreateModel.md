# NewsCreateModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**title** | **str** | The headline of the news | [optional] [readonly] 
**summary** | **str** | A short summary | [optional] [readonly] 
**description** | [**Formattable**](Formattable.md) | The main body of the news with all the details | [optional] 
**links** | [**NewsCreateModelLinks**](NewsCreateModelLinks.md) |  | [optional] 

## Example

```python
from openproject_client.models.news_create_model import NewsCreateModel

# TODO update the JSON string below
json = "{}"
# create an instance of NewsCreateModel from a JSON string
news_create_model_instance = NewsCreateModel.from_json(json)
# print the JSON string representation of the object
print(NewsCreateModel.to_json())

# convert the object into a dict
news_create_model_dict = news_create_model_instance.to_dict()
# create an instance of NewsCreateModel from a dict
news_create_model_from_dict = NewsCreateModel.from_dict(news_create_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


