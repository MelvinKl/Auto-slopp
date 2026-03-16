# UserModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**id** | **int** | The principal&#39;s unique identifier. | 
**name** | **str** | The principal&#39;s display name, layout depends on instance settings. | 
**created_at** | **datetime** | Time of creation | [optional] 
**updated_at** | **datetime** | Time of the most recent change to the user | [optional] 
**links** | [**UserModelAllOfLinks**](UserModelAllOfLinks.md) |  | 
**avatar** | **str** | URL to user&#39;s avatar | 
**login** | **str** | The user&#39;s login name  # Conditions  - User is self, or &#x60;create_user&#x60; or &#x60;manage_user&#x60; permission globally | [optional] 
**first_name** | **str** | The user&#39;s first name  # Conditions  - User is self, or &#x60;create_user&#x60; or &#x60;manage_user&#x60; permission globally | [optional] 
**last_name** | **str** | The user&#39;s last name  # Conditions  - User is self, or &#x60;create_user&#x60; or &#x60;manage_user&#x60; permission globally | [optional] 
**email** | **str** | The user&#39;s email address  # Conditions  - E-Mail address not hidden - User is not a new record - User is self, or &#x60;create_user&#x60; or &#x60;manage_user&#x60; permission globally | [optional] 
**admin** | **bool** | Flag indicating whether or not the user is an admin  # Conditions  - &#x60;admin&#x60; | [optional] 
**status** | **str** | The current activation status of the user.  # Conditions  - User is self, or &#x60;create_user&#x60; or &#x60;manage_user&#x60; permission globally | [optional] 
**language** | **str** | User&#39;s language | ISO 639-1 format  # Conditions  - User is self, or &#x60;create_user&#x60; or &#x60;manage_user&#x60; permission globally | [optional] 
**identity_url** | **str** | User&#39;s identity_url for OmniAuth authentication. **Deprecated:** It will be removed in the near future.  # Conditions  - User is self, or &#x60;create_user&#x60; or &#x60;manage_user&#x60; permission globally | [optional] 

## Example

```python
from auto_slopp.openproject.openapi_client.models.user_model import UserModel

# TODO update the JSON string below
json = "{}"
# create an instance of UserModel from a JSON string
user_model_instance = UserModel.from_json(json)
# print the JSON string representation of the object
print(UserModel.to_json())

# convert the object into a dict
user_model_dict = user_model_instance.to_dict()
# create an instance of UserModel from a dict
user_model_from_dict = UserModel.from_dict(user_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


