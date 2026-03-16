# WorkspacesSchemaModel

A schema for a workspace. This schema defines the attributes of a workspace.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** | The type identifier for this resource | [optional] 
**dependencies** | **List[object]** | Schema dependencies (currently empty for workspaces) | [optional] 
**attribute_groups** | [**List[WorkspacesSchemaModelAttributeGroupsInner]**](WorkspacesSchemaModelAttributeGroupsInner.md) | Defines the organizational structure of project custom fields into sections for UI rendering.  Each attribute group represents a project attribute section containing related project attributes. The sections determine how project attributes are visually organized and grouped in forms.  **Key behaviors:** - Admin-only project attributes appear only for users with admin privileges - Empty sections (with no accessible project attributes) are omitted from the response - The order reflects the configured section positioning in admin settings - Each section contains only project attributes assigned to that specific section  **Example structure:** &#x60;&#x60;&#x60;json [   {     \&quot;_type\&quot;: \&quot;ProjectFormCustomFieldSection\&quot;,     \&quot;name\&quot;: \&quot;Project Details\&quot;,     \&quot;attributes\&quot;: [\&quot;customField1\&quot;, \&quot;customField3\&quot;]   },   {     \&quot;_type\&quot;: \&quot;ProjectFormCustomFieldSection\&quot;,     \&quot;name\&quot;: \&quot;Budget Information\&quot;,     \&quot;attributes\&quot;: [\&quot;customField2\&quot;, \&quot;customField4\&quot;]   } ] &#x60;&#x60;&#x60; | [optional] 
**id** | [**SchemaPropertyModel**](SchemaPropertyModel.md) |  | [optional] 
**name** | [**SchemaPropertyModel**](SchemaPropertyModel.md) |  | [optional] 
**identifier** | [**SchemaPropertyModel**](SchemaPropertyModel.md) |  | [optional] 
**description** | [**SchemaPropertyModel**](SchemaPropertyModel.md) |  | [optional] 
**public** | [**SchemaPropertyModel**](SchemaPropertyModel.md) |  | [optional] 
**active** | [**SchemaPropertyModel**](SchemaPropertyModel.md) |  | [optional] 
**status** | [**SchemaPropertyModel**](SchemaPropertyModel.md) |  | [optional] 
**status_explanation** | [**SchemaPropertyModel**](SchemaPropertyModel.md) |  | [optional] 
**parent** | [**SchemaPropertyModel**](SchemaPropertyModel.md) |  | [optional] 
**created_at** | [**SchemaPropertyModel**](SchemaPropertyModel.md) |  | [optional] 
**updated_at** | [**SchemaPropertyModel**](SchemaPropertyModel.md) |  | [optional] 
**links** | [**WorkspacesSchemaModelLinks**](WorkspacesSchemaModelLinks.md) |  | [optional] 

## Example

```python
from openproject_client.models.workspaces_schema_model import WorkspacesSchemaModel

# TODO update the JSON string below
json = "{}"
# create an instance of WorkspacesSchemaModel from a JSON string
workspaces_schema_model_instance = WorkspacesSchemaModel.from_json(json)
# print the JSON string representation of the object
print(WorkspacesSchemaModel.to_json())

# convert the object into a dict
workspaces_schema_model_dict = workspaces_schema_model_instance.to_dict()
# create an instance of WorkspacesSchemaModel from a dict
workspaces_schema_model_from_dict = WorkspacesSchemaModel.from_dict(workspaces_schema_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


