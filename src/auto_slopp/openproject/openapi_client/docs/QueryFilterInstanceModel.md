# QueryFilterInstanceModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**links** | [**QueryFilterInstanceModelLinks**](QueryFilterInstanceModelLinks.md) |  | 
**type** | **str** |  | 
**name** | **str** |  | 

## Example

```python
from auto_slopp.openproject.openapi_client.models.query_filter_instance_model import QueryFilterInstanceModel

# TODO update the JSON string below
json = "{}"
# create an instance of QueryFilterInstanceModel from a JSON string
query_filter_instance_model_instance = QueryFilterInstanceModel.from_json(json)
# print the JSON string representation of the object
print(QueryFilterInstanceModel.to_json())

# convert the object into a dict
query_filter_instance_model_dict = query_filter_instance_model_instance.to_dict()
# create an instance of QueryFilterInstanceModel from a dict
query_filter_instance_model_from_dict = QueryFilterInstanceModel.from_dict(query_filter_instance_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


