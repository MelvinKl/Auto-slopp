# PlaceholderUserModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**id** | **int** | The principal&#39;s unique identifier. | 
**name** | **str** | The principal&#39;s display name, layout depends on instance settings. | 
**created_at** | **datetime** | Time of creation | [optional] 
**updated_at** | **datetime** | Time of the most recent change to the principal | [optional] 
**links** | [**PlaceholderUserModelAllOfLinks**](PlaceholderUserModelAllOfLinks.md) |  | 
**status** | **str** | The current activation status of the placeholder user.  # Conditions  - User has &#x60;manage_placeholder_user&#x60; permission globally | [optional] 

## Example

```python
from openproject_client.models.placeholder_user_model import PlaceholderUserModel

# TODO update the JSON string below
json = "{}"
# create an instance of PlaceholderUserModel from a JSON string
placeholder_user_model_instance = PlaceholderUserModel.from_json(json)
# print the JSON string representation of the object
print(PlaceholderUserModel.to_json())

# convert the object into a dict
placeholder_user_model_dict = placeholder_user_model_instance.to_dict()
# create an instance of PlaceholderUserModel from a dict
placeholder_user_model_from_dict = PlaceholderUserModel.from_dict(placeholder_user_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


