# QueryFilterInstanceModelLinks


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**filter** | [**Link**](Link.md) |  | 
**var_schema** | [**Link**](Link.md) |  | 
**operator** | [**Link**](Link.md) |  | [optional] 

## Example

```python
from auto_slopp.openproject.openapi_client.models.query_filter_instance_model_links import QueryFilterInstanceModelLinks

# TODO update the JSON string below
json = "{}"
# create an instance of QueryFilterInstanceModelLinks from a JSON string
query_filter_instance_model_links_instance = QueryFilterInstanceModelLinks.from_json(json)
# print the JSON string representation of the object
print(QueryFilterInstanceModelLinks.to_json())

# convert the object into a dict
query_filter_instance_model_links_dict = query_filter_instance_model_links_instance.to_dict()
# create an instance of QueryFilterInstanceModelLinks from a dict
query_filter_instance_model_links_from_dict = QueryFilterInstanceModelLinks.from_dict(query_filter_instance_model_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


