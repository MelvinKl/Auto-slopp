# UserCreateModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**admin** | **bool** |  | 
**email** | **str** |  | 
**login** | **str** |  | 
**password** | **str** | The users password.  *Conditions:*  Only writable on creation, not on update. | [optional] 
**first_name** | **str** |  | 
**last_name** | **str** |  | 
**status** | **str** | The current activation status of the user.  *Conditions:*  Only writable on creation, not on update. | [optional] 
**language** | **str** |  | 

## Example

```python
from openproject_client.models.user_create_model import UserCreateModel

# TODO update the JSON string below
json = "{}"
# create an instance of UserCreateModel from a JSON string
user_create_model_instance = UserCreateModel.from_json(json)
# print the JSON string representation of the object
print(UserCreateModel.to_json())

# convert the object into a dict
user_create_model_dict = user_create_model_instance.to_dict()
# create an instance of UserCreateModel from a dict
user_create_model_from_dict = UserCreateModel.from_dict(user_create_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


