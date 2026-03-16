# CreateViewsRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**links** | [**CreateViewsRequestLinks**](CreateViewsRequestLinks.md) |  | [optional] 

## Example

```python
from openproject_client.models.create_views_request import CreateViewsRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateViewsRequest from a JSON string
create_views_request_instance = CreateViewsRequest.from_json(json)
# print the JSON string representation of the object
print(CreateViewsRequest.to_json())

# convert the object into a dict
create_views_request_dict = create_views_request_instance.to_dict()
# create an instance of CreateViewsRequest from a dict
create_views_request_from_dict = CreateViewsRequest.from_dict(create_views_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


