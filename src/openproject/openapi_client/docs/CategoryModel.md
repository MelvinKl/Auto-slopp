# CategoryModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** | Category id | [optional] [readonly] 
**name** | **str** | Category name | [optional] 
**links** | [**CategoryModelLinks**](CategoryModelLinks.md) |  | [optional] 

## Example

```python
from openproject_client.models.category_model import CategoryModel

# TODO update the JSON string below
json = "{}"
# create an instance of CategoryModel from a JSON string
category_model_instance = CategoryModel.from_json(json)
# print the JSON string representation of the object
print(CategoryModel.to_json())

# convert the object into a dict
category_model_dict = category_model_instance.to_dict()
# create an instance of CategoryModel from a dict
category_model_from_dict = CategoryModel.from_dict(category_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


