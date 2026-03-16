# WorkPackageSchemaModelLinks


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_self** | [**Link**](Link.md) | This work package schema  **Resource**: Schema | [optional] 

## Example

```python
from openproject_client.models.work_package_schema_model_links import WorkPackageSchemaModelLinks

# TODO update the JSON string below
json = "{}"
# create an instance of WorkPackageSchemaModelLinks from a JSON string
work_package_schema_model_links_instance = WorkPackageSchemaModelLinks.from_json(json)
# print the JSON string representation of the object
print(WorkPackageSchemaModelLinks.to_json())

# convert the object into a dict
work_package_schema_model_links_dict = work_package_schema_model_links_instance.to_dict()
# create an instance of WorkPackageSchemaModelLinks from a dict
work_package_schema_model_links_from_dict = WorkPackageSchemaModelLinks.from_dict(work_package_schema_model_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


