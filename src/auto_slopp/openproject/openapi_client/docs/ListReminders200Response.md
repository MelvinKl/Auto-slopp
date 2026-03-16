# ListReminders200Response


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**total** | **int** | The total amount of elements available in the collection. | 
**count** | **int** | Actual amount of elements in this response. | 
**embedded** | [**ListReminders200ResponseEmbedded**](ListReminders200ResponseEmbedded.md) |  | 

## Example

```python
from auto_slopp.openproject.openapi_client.models.list_reminders200_response import ListReminders200Response

# TODO update the JSON string below
json = "{}"
# create an instance of ListReminders200Response from a JSON string
list_reminders200_response_instance = ListReminders200Response.from_json(json)
# print the JSON string representation of the object
print(ListReminders200Response.to_json())

# convert the object into a dict
list_reminders200_response_dict = list_reminders200_response_instance.to_dict()
# create an instance of ListReminders200Response from a dict
list_reminders200_response_from_dict = ListReminders200Response.from_dict(list_reminders200_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


