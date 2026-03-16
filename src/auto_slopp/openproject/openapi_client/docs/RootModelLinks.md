# RootModelLinks


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_self** | [**Link**](Link.md) | This root information object.  **Resource**: Root | 
**configuration** | [**Link**](Link.md) | The configuration resource.  **Resource**: Configuration | 
**memberships** | [**Link**](Link.md) | The collection of memberships.  **Resource**: Collection | 
**priorities** | [**Link**](Link.md) | The collection of priorities.  **Resource**: Collection | 
**relations** | [**Link**](Link.md) | The collection of relations.  **Resource**: Collection | 
**statuses** | [**Link**](Link.md) | The collection of statuses.  **Resource**: Collection | 
**time_entries** | [**Link**](Link.md) | The collection of time entries.  **Resource**: Collection | 
**types** | [**Link**](Link.md) | The collection of types.  **Resource**: Collection | 
**user** | [**Link**](Link.md) | The current user resource.  **Resource**: User | 
**user_preferences** | [**Link**](Link.md) | The current user preferences resource.  **Resource**: UserPreferences | 
**work_packages** | [**Link**](Link.md) | The work package collection.  **Resource**: Collection | 

## Example

```python
from auto_slopp.openproject.openapi_client.models.root_model_links import RootModelLinks

# TODO update the JSON string below
json = "{}"
# create an instance of RootModelLinks from a JSON string
root_model_links_instance = RootModelLinks.from_json(json)
# print the JSON string representation of the object
print(RootModelLinks.to_json())

# convert the object into a dict
root_model_links_dict = root_model_links_instance.to_dict()
# create an instance of RootModelLinks from a dict
root_model_links_from_dict = RootModelLinks.from_dict(root_model_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


