# WorkPackageFormModelEmbedded


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**payload** | [**WorkPackageWriteModel**](WorkPackageWriteModel.md) |  | [optional] 
**var_schema** | [**WorkPackageSchemaModel**](WorkPackageSchemaModel.md) |  | [optional] 
**validation_errors** | **object** | All validation errors, where the key is the faulty property. The object is empty, if the request body is valid. | [optional] 

## Example

```python
from openproject_client.models.work_package_form_model_embedded import WorkPackageFormModelEmbedded

# TODO update the JSON string below
json = "{}"
# create an instance of WorkPackageFormModelEmbedded from a JSON string
work_package_form_model_embedded_instance = WorkPackageFormModelEmbedded.from_json(json)
# print the JSON string representation of the object
print(WorkPackageFormModelEmbedded.to_json())

# convert the object into a dict
work_package_form_model_embedded_dict = work_package_form_model_embedded_instance.to_dict()
# create an instance of WorkPackageFormModelEmbedded from a dict
work_package_form_model_embedded_from_dict = WorkPackageFormModelEmbedded.from_dict(work_package_form_model_embedded_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


