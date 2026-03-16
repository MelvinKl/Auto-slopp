# ProjectConfigurationModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**maximum_attachment_file_size** | **int** | The maximum allowed size of an attachment in Bytes | [optional] [readonly] 
**host_name** | **str** | The host name configured for the system | [optional] [readonly] 
**per_page_options** | **List[int]** | Page size steps to be offered in paginated list UI | [optional] 
**duration_format** | **str** | The format used to display Work, Remaining Work, and Spent time durations | [optional] [readonly] 
**active_feature_flags** | **List[str]** | The list of all feature flags that are active | [optional] 
**enabled_internal_comments** | **bool** | Whether internal comments are enabled for this project | [optional] [readonly] 

## Example

```python
from auto_slopp.openproject.openapi_client.models.project_configuration_model import ProjectConfigurationModel

# TODO update the JSON string below
json = "{}"
# create an instance of ProjectConfigurationModel from a JSON string
project_configuration_model_instance = ProjectConfigurationModel.from_json(json)
# print the JSON string representation of the object
print(ProjectConfigurationModel.to_json())

# convert the object into a dict
project_configuration_model_dict = project_configuration_model_instance.to_dict()
# create an instance of ProjectConfigurationModel from a dict
project_configuration_model_from_dict = ProjectConfigurationModel.from_dict(project_configuration_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


