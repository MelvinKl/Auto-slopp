# WorkspacesSchemaModelAttributeGroupsInner


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** | The type identifier for this resource | [optional] 
**id** | **int** | The unique identifier of the custom field section | [optional] 
**name** | **str** | The human-readable name of the custom field section | [optional] 
**attributes** | **List[str]** | Array of camelCase custom field attribute names belonging to this section. Only includes custom fields visible to the current user. | [optional] 

## Example

```python
from auto_slopp.openproject.openapi_client.models.workspaces_schema_model_attribute_groups_inner import WorkspacesSchemaModelAttributeGroupsInner

# TODO update the JSON string below
json = "{}"
# create an instance of WorkspacesSchemaModelAttributeGroupsInner from a JSON string
workspaces_schema_model_attribute_groups_inner_instance = WorkspacesSchemaModelAttributeGroupsInner.from_json(json)
# print the JSON string representation of the object
print(WorkspacesSchemaModelAttributeGroupsInner.to_json())

# convert the object into a dict
workspaces_schema_model_attribute_groups_inner_dict = workspaces_schema_model_attribute_groups_inner_instance.to_dict()
# create an instance of WorkspacesSchemaModelAttributeGroupsInner from a dict
workspaces_schema_model_attribute_groups_inner_from_dict = WorkspacesSchemaModelAttributeGroupsInner.from_dict(workspaces_schema_model_attribute_groups_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


