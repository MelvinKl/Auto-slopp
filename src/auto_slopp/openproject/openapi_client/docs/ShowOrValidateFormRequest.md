# ShowOrValidateFormRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | [optional] 
**lock_version** | **float** |  | [optional] 
**subject** | **str** |  | [optional] 

## Example

```python
from auto_slopp.openproject.openapi_client.models.show_or_validate_form_request import ShowOrValidateFormRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ShowOrValidateFormRequest from a JSON string
show_or_validate_form_request_instance = ShowOrValidateFormRequest.from_json(json)
# print the JSON string representation of the object
print(ShowOrValidateFormRequest.to_json())

# convert the object into a dict
show_or_validate_form_request_dict = show_or_validate_form_request_instance.to_dict()
# create an instance of ShowOrValidateFormRequest from a dict
show_or_validate_form_request_from_dict = ShowOrValidateFormRequest.from_dict(show_or_validate_form_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


