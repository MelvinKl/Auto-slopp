# WorkPackageFormModelLinks


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_self** | [**Link**](Link.md) | This form endpoint  **Resource** : Form | [optional] 
**validate** | [**Link**](Link.md) | The endpoint for validating the request bodies. Often referring to this very form endpoint. | [optional] 
**preview_markup** | [**Link**](Link.md) | Renders a markup preview for the work package form. | [optional] 
**custom_fields** | [**Link**](Link.md) | Link to the HTML page for the custom field definitions. | [optional] 
**configure_form** | [**Link**](Link.md) | Link to the HTML page for the form configuration. | [optional] 

## Example

```python
from auto_slopp.openproject.openapi_client.models.work_package_form_model_links import WorkPackageFormModelLinks

# TODO update the JSON string below
json = "{}"
# create an instance of WorkPackageFormModelLinks from a JSON string
work_package_form_model_links_instance = WorkPackageFormModelLinks.from_json(json)
# print the JSON string representation of the object
print(WorkPackageFormModelLinks.to_json())

# convert the object into a dict
work_package_form_model_links_dict = work_package_form_model_links_instance.to_dict()
# create an instance of WorkPackageFormModelLinks from a dict
work_package_form_model_links_from_dict = WorkPackageFormModelLinks.from_dict(work_package_form_model_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


