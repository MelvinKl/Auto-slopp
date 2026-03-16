# QuerySortByModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | QuerySortBy id | [readonly] 
**name** | **str** | QuerySortBy name | 

## Example

```python
from openproject_client.models.query_sort_by_model import QuerySortByModel

# TODO update the JSON string below
json = "{}"
# create an instance of QuerySortByModel from a JSON string
query_sort_by_model_instance = QuerySortByModel.from_json(json)
# print the JSON string representation of the object
print(QuerySortByModel.to_json())

# convert the object into a dict
query_sort_by_model_dict = query_sort_by_model_instance.to_dict()
# create an instance of QuerySortByModel from a dict
query_sort_by_model_from_dict = QuerySortByModel.from_dict(query_sort_by_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


