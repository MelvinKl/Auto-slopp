# UpdateUserPreferencesRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**auto_hide_popups** | **bool** |  | [optional] 
**time_zone** | **str** |  | [optional] 

## Example

```python
from openproject_client.models.update_user_preferences_request import UpdateUserPreferencesRequest

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateUserPreferencesRequest from a JSON string
update_user_preferences_request_instance = UpdateUserPreferencesRequest.from_json(json)
# print the JSON string representation of the object
print(UpdateUserPreferencesRequest.to_json())

# convert the object into a dict
update_user_preferences_request_dict = update_user_preferences_request_instance.to_dict()
# create an instance of UpdateUserPreferencesRequest from a dict
update_user_preferences_request_from_dict = UpdateUserPreferencesRequest.from_dict(update_user_preferences_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


