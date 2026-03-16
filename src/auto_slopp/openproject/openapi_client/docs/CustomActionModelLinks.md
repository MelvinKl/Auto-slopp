# CustomActionModelLinks


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_self** | [**Link**](Link.md) | This custom action  **Resource**: CustomAction | 
**execute_immediately** | [**Link**](Link.md) | Execute this custom action. | 

## Example

```python
from auto_slopp.openproject.openapi_client.models.custom_action_model_links import CustomActionModelLinks

# TODO update the JSON string below
json = "{}"
# create an instance of CustomActionModelLinks from a JSON string
custom_action_model_links_instance = CustomActionModelLinks.from_json(json)
# print the JSON string representation of the object
print(CustomActionModelLinks.to_json())

# convert the object into a dict
custom_action_model_links_dict = custom_action_model_links_instance.to_dict()
# create an instance of CustomActionModelLinks from a dict
custom_action_model_links_from_dict = CustomActionModelLinks.from_dict(custom_action_model_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


