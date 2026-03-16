# ConfigurationModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**maximum_attachment_file_size** | **int** | The maximum allowed size of an attachment in Bytes | [optional] [readonly] 
**host_name** | **str** | The host name configured for the system | [optional] [readonly] 
**per_page_options** | **List[int]** | Page size steps to be offered in paginated list UI | [optional] 
**duration_format** | **str** | The format used to display Work, Remaining Work, and Spent time durations | [optional] [readonly] 
**active_feature_flags** | **List[str]** | The list of all feature flags that are active | [optional] 

## Example

```python
from auto_slopp.openproject.openapi_client.models.configuration_model import ConfigurationModel

# TODO update the JSON string below
json = "{}"
# create an instance of ConfigurationModel from a JSON string
configuration_model_instance = ConfigurationModel.from_json(json)
# print the JSON string representation of the object
print(ConfigurationModel.to_json())

# convert the object into a dict
configuration_model_dict = configuration_model_instance.to_dict()
# create an instance of ConfigurationModel from a dict
configuration_model_from_dict = ConfigurationModel.from_dict(configuration_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


