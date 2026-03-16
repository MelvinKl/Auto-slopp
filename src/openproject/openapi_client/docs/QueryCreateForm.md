# QueryCreateForm


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Query name. | [optional] 

## Example

```python
from openproject_client.models.query_create_form import QueryCreateForm

# TODO update the JSON string below
json = "{}"
# create an instance of QueryCreateForm from a JSON string
query_create_form_instance = QueryCreateForm.from_json(json)
# print the JSON string representation of the object
print(QueryCreateForm.to_json())

# convert the object into a dict
query_create_form_dict = query_create_form_instance.to_dict()
# create an instance of QueryCreateForm from a dict
query_create_form_from_dict = QueryCreateForm.from_dict(query_create_form_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


