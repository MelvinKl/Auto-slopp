# QueryModelLinks


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**star** | [**Link**](Link.md) | Elevates the query to the status of &#39;starred&#39;  # Conditions  **Permission**: save queries for own queries, manage public queries for public queries; Only present if query is not yet starred | [optional] [readonly] 
**unstar** | [**Link**](Link.md) | Removes the &#39;starred&#39; status  # Conditions  **Permission**: save queries for own queries, manage public queries for public queries; Only present if query is starred | [optional] [readonly] 
**update** | [**Link**](Link.md) | Use the Form based process to verify the query before persisting  # Conditions  **Permission**: view work packages | [optional] [readonly] 
**update_immediately** | [**Link**](Link.md) | Persist the query without using a Form based process for guidance  # Conditions  **Permission**: save queries for own queries, manage public queries for public queries; | [optional] [readonly] 

## Example

```python
from auto_slopp.openproject.openapi_client.models.query_model_links import QueryModelLinks

# TODO update the JSON string below
json = "{}"
# create an instance of QueryModelLinks from a JSON string
query_model_links_instance = QueryModelLinks.from_json(json)
# print the JSON string representation of the object
print(QueryModelLinks.to_json())

# convert the object into a dict
query_model_links_dict = query_model_links_instance.to_dict()
# create an instance of QueryModelLinks from a dict
query_model_links_from_dict = QueryModelLinks.from_dict(query_model_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


