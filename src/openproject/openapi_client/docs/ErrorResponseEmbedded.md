# ErrorResponseEmbedded


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**details** | [**ErrorResponseEmbeddedDetails**](ErrorResponseEmbeddedDetails.md) |  | [optional] 

## Example

```python
from openproject_client.models.error_response_embedded import ErrorResponseEmbedded

# TODO update the JSON string below
json = "{}"
# create an instance of ErrorResponseEmbedded from a JSON string
error_response_embedded_instance = ErrorResponseEmbedded.from_json(json)
# print the JSON string representation of the object
print(ErrorResponseEmbedded.to_json())

# convert the object into a dict
error_response_embedded_dict = error_response_embedded_instance.to_dict()
# create an instance of ErrorResponseEmbedded from a dict
error_response_embedded_from_dict = ErrorResponseEmbedded.from_dict(error_response_embedded_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


