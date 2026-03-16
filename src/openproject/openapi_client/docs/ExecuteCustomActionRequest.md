# ExecuteCustomActionRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**links** | [**ExecuteCustomActionRequestLinks**](ExecuteCustomActionRequestLinks.md) |  | [optional] 
**lock_version** | **str** |  | [optional] 

## Example

```python
from openproject_client.models.execute_custom_action_request import ExecuteCustomActionRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ExecuteCustomActionRequest from a JSON string
execute_custom_action_request_instance = ExecuteCustomActionRequest.from_json(json)
# print the JSON string representation of the object
print(ExecuteCustomActionRequest.to_json())

# convert the object into a dict
execute_custom_action_request_dict = execute_custom_action_request_instance.to_dict()
# create an instance of ExecuteCustomActionRequest from a dict
execute_custom_action_request_from_dict = ExecuteCustomActionRequest.from_dict(execute_custom_action_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


