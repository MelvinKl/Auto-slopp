# QueryColumnModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | Query column id | [readonly] 
**name** | **str** | Query column name | 

## Example

```python
from auto_slopp.openproject.openapi_client.models.query_column_model import QueryColumnModel

# TODO update the JSON string below
json = "{}"
# create an instance of QueryColumnModel from a JSON string
query_column_model_instance = QueryColumnModel.from_json(json)
# print the JSON string representation of the object
print(QueryColumnModel.to_json())

# convert the object into a dict
query_column_model_dict = query_column_model_instance.to_dict()
# create an instance of QueryColumnModel from a dict
query_column_model_from_dict = QueryColumnModel.from_dict(query_column_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


