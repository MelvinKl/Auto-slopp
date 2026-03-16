# WorkPackageWriteModelMeta

Meta information for the work package request

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**validate_custom_fields** | **bool** | When set to true, explicitly validates all required custom fields on the work package, regardless of whether they are provided in the request body. This overrides the default behavior where only custom fields included in the request are validated. Use this parameter when you need to ensure all required custom fields have valid values before allowing the update to proceed. | [optional] [default to False]

## Example

```python
from openproject_client.models.work_package_write_model_meta import WorkPackageWriteModelMeta

# TODO update the JSON string below
json = "{}"
# create an instance of WorkPackageWriteModelMeta from a JSON string
work_package_write_model_meta_instance = WorkPackageWriteModelMeta.from_json(json)
# print the JSON string representation of the object
print(WorkPackageWriteModelMeta.to_json())

# convert the object into a dict
work_package_write_model_meta_dict = work_package_write_model_meta_instance.to_dict()
# create an instance of WorkPackageWriteModelMeta from a dict
work_package_write_model_meta_from_dict = WorkPackageWriteModelMeta.from_dict(work_package_write_model_meta_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


