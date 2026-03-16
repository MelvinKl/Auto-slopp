# PlaceholderUserModelAllOfLinks


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**show_user** | [**Link**](Link.md) | A relative path to show the placeholder user in the web application. | 
**delete** | [**Link**](Link.md) | An href to delete the placeholder user.  # Conditions:  - &#x60;manage_placeholder_user&#x60; | [optional] 
**update_immediately** | [**Link**](Link.md) | An href to update the placeholder user.  # Conditions:  - &#x60;manage_placeholder_user&#x60;  **Resource**: PlaceholderUser | [optional] 

## Example

```python
from auto_slopp.openproject.openapi_client.models.placeholder_user_model_all_of_links import PlaceholderUserModelAllOfLinks

# TODO update the JSON string below
json = "{}"
# create an instance of PlaceholderUserModelAllOfLinks from a JSON string
placeholder_user_model_all_of_links_instance = PlaceholderUserModelAllOfLinks.from_json(json)
# print the JSON string representation of the object
print(PlaceholderUserModelAllOfLinks.to_json())

# convert the object into a dict
placeholder_user_model_all_of_links_dict = placeholder_user_model_all_of_links_instance.to_dict()
# create an instance of PlaceholderUserModelAllOfLinks from a dict
placeholder_user_model_all_of_links_from_dict = PlaceholderUserModelAllOfLinks.from_dict(placeholder_user_model_all_of_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


