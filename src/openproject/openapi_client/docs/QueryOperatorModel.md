# QueryOperatorModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | Query operator id | [readonly] 
**name** | **str** | Query operator name | 

## Example

```python
from openproject_client.models.query_operator_model import QueryOperatorModel

# TODO update the JSON string below
json = "{}"
# create an instance of QueryOperatorModel from a JSON string
query_operator_model_instance = QueryOperatorModel.from_json(json)
# print the JSON string representation of the object
print(QueryOperatorModel.to_json())

# convert the object into a dict
query_operator_model_dict = query_operator_model_instance.to_dict()
# create an instance of QueryOperatorModel from a dict
query_operator_model_from_dict = QueryOperatorModel.from_dict(query_operator_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


