# QueryFilterInstanceSchemaModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Describes the name attribute | [readonly] 
**links** | [**QueryFilterInstanceSchemaModelLinks**](QueryFilterInstanceSchemaModelLinks.md) |  | 

## Example

```python
from openproject_client.models.query_filter_instance_schema_model import QueryFilterInstanceSchemaModel

# TODO update the JSON string below
json = "{}"
# create an instance of QueryFilterInstanceSchemaModel from a JSON string
query_filter_instance_schema_model_instance = QueryFilterInstanceSchemaModel.from_json(json)
# print the JSON string representation of the object
print(QueryFilterInstanceSchemaModel.to_json())

# convert the object into a dict
query_filter_instance_schema_model_dict = query_filter_instance_schema_model_instance.to_dict()
# create an instance of QueryFilterInstanceSchemaModel from a dict
query_filter_instance_schema_model_from_dict = QueryFilterInstanceSchemaModel.from_dict(query_filter_instance_schema_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


