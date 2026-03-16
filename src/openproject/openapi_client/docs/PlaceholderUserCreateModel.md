# PlaceholderUserCreateModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | The new name of the placeholder user to be created. | [optional] 

## Example

```python
from openproject_client.models.placeholder_user_create_model import PlaceholderUserCreateModel

# TODO update the JSON string below
json = "{}"
# create an instance of PlaceholderUserCreateModel from a JSON string
placeholder_user_create_model_instance = PlaceholderUserCreateModel.from_json(json)
# print the JSON string representation of the object
print(PlaceholderUserCreateModel.to_json())

# convert the object into a dict
placeholder_user_create_model_dict = placeholder_user_create_model_instance.to_dict()
# create an instance of PlaceholderUserCreateModel from a dict
placeholder_user_create_model_from_dict = PlaceholderUserCreateModel.from_dict(placeholder_user_create_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


