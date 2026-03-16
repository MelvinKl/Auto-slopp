# AddWatcherRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**user** | [**ExecuteCustomActionRequestLinksWorkPackage**](ExecuteCustomActionRequestLinksWorkPackage.md) |  | [optional] 

## Example

```python
from openproject_client.models.add_watcher_request import AddWatcherRequest

# TODO update the JSON string below
json = "{}"
# create an instance of AddWatcherRequest from a JSON string
add_watcher_request_instance = AddWatcherRequest.from_json(json)
# print the JSON string representation of the object
print(AddWatcherRequest.to_json())

# convert the object into a dict
add_watcher_request_dict = add_watcher_request_instance.to_dict()
# create an instance of AddWatcherRequest from a dict
add_watcher_request_from_dict = AddWatcherRequest.from_dict(add_watcher_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


