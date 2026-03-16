# CategoryModelLinks


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_self** | [**Link**](Link.md) | This category  **Resource**: Category | [readonly] 
**project** | [**Link**](Link.md) | The project of this category  **Resource**: Project | [readonly] 
**default_assignee** | [**Link**](Link.md) | Default assignee for work packages of this category  **Resource**: User | [optional] [readonly] 

## Example

```python
from openproject_client.models.category_model_links import CategoryModelLinks

# TODO update the JSON string below
json = "{}"
# create an instance of CategoryModelLinks from a JSON string
category_model_links_instance = CategoryModelLinks.from_json(json)
# print the JSON string representation of the object
print(CategoryModelLinks.to_json())

# convert the object into a dict
category_model_links_dict = category_model_links_instance.to_dict()
# create an instance of CategoryModelLinks from a dict
category_model_links_from_dict = CategoryModelLinks.from_dict(category_model_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


