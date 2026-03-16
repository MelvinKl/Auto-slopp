# QueryFilterInstanceSchemaModelLinks


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_self** | [**Link**](Link.md) | This QueryFilterInstanceSchema (same as for schema)  **Resource**: QueryFilterInstanceSchema | [readonly] 
**filter** | [**Link**](Link.md) | The filter for which this schema is specific  **Resource**: Filter | [readonly] 

## Example

```python
from auto_slopp.openproject.openapi_client.models.query_filter_instance_schema_model_links import QueryFilterInstanceSchemaModelLinks

# TODO update the JSON string below
json = "{}"
# create an instance of QueryFilterInstanceSchemaModelLinks from a JSON string
query_filter_instance_schema_model_links_instance = QueryFilterInstanceSchemaModelLinks.from_json(json)
# print the JSON string representation of the object
print(QueryFilterInstanceSchemaModelLinks.to_json())

# convert the object into a dict
query_filter_instance_schema_model_links_dict = query_filter_instance_schema_model_links_instance.to_dict()
# create an instance of QueryFilterInstanceSchemaModelLinks from a dict
query_filter_instance_schema_model_links_from_dict = QueryFilterInstanceSchemaModelLinks.from_dict(query_filter_instance_schema_model_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


