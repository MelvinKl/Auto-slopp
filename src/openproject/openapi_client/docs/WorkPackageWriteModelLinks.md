# WorkPackageWriteModelLinks


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**category** | [**Link**](Link.md) | The category of the work package  **Resource**: Category | [optional] 
**type** | [**Link**](Link.md) | The type of the work package  **Resource**: Type | [optional] 
**priority** | [**Link**](Link.md) | The priority of the work package  **Resource**: Priority | [optional] 
**project** | [**Link**](Link.md) | The project to which the work package belongs  **Resource**: Project | [optional] 
**status** | [**Link**](Link.md) | The current status of the work package  **Resource**: Status | [optional] 
**responsible** | [**Link**](Link.md) | The person that is responsible for the overall outcome  **Resource**: User | [optional] 
**assignee** | [**Link**](Link.md) | The person that is intended to work on the work package  **Resource**: User | [optional] 
**version** | [**Link**](Link.md) | The version associated to the work package  **Resource**: Version | [optional] 
**parent** | [**Link**](Link.md) | Parent work package  **Resource**: WorkPackage | [optional] 

## Example

```python
from openproject_client.models.work_package_write_model_links import WorkPackageWriteModelLinks

# TODO update the JSON string below
json = "{}"
# create an instance of WorkPackageWriteModelLinks from a JSON string
work_package_write_model_links_instance = WorkPackageWriteModelLinks.from_json(json)
# print the JSON string representation of the object
print(WorkPackageWriteModelLinks.to_json())

# convert the object into a dict
work_package_write_model_links_dict = work_package_write_model_links_instance.to_dict()
# create an instance of WorkPackageWriteModelLinks from a dict
work_package_write_model_links_from_dict = WorkPackageWriteModelLinks.from_dict(work_package_write_model_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


