# ExecuteCustomActionRequestLinks


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**work_package** | [**ExecuteCustomActionRequestLinksWorkPackage**](ExecuteCustomActionRequestLinksWorkPackage.md) |  | [optional] 

## Example

```python
from auto_slopp.openproject.openapi_client.models.execute_custom_action_request_links import ExecuteCustomActionRequestLinks

# TODO update the JSON string below
json = "{}"
# create an instance of ExecuteCustomActionRequestLinks from a JSON string
execute_custom_action_request_links_instance = ExecuteCustomActionRequestLinks.from_json(json)
# print the JSON string representation of the object
print(ExecuteCustomActionRequestLinks.to_json())

# convert the object into a dict
execute_custom_action_request_links_dict = execute_custom_action_request_links_instance.to_dict()
# create an instance of ExecuteCustomActionRequestLinks from a dict
execute_custom_action_request_links_from_dict = ExecuteCustomActionRequestLinks.from_dict(execute_custom_action_request_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


