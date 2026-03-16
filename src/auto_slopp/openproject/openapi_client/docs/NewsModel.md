# NewsModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** | News&#39; id | [optional] [readonly] 
**title** | **str** | The headline of the news | [optional] [readonly] 
**summary** | **str** | A short summary | [optional] [readonly] 
**description** | [**Formattable**](Formattable.md) | The main body of the news with all the details | [optional] [readonly] 
**created_at** | **datetime** | The time the news was created at | [optional] [readonly] 
**links** | [**NewsModelLinks**](NewsModelLinks.md) |  | [optional] 

## Example

```python
from auto_slopp.openproject.openapi_client.models.news_model import NewsModel

# TODO update the JSON string below
json = "{}"
# create an instance of NewsModel from a JSON string
news_model_instance = NewsModel.from_json(json)
# print the JSON string representation of the object
print(NewsModel.to_json())

# convert the object into a dict
news_model_dict = news_model_instance.to_dict()
# create an instance of NewsModel from a dict
news_model_from_dict = NewsModel.from_dict(news_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


