# HierarchyItemReadModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**id** | **int** | Hierarchy item identifier | 
**label** | **str** | The label of the hierarchy item | 
**short** | **str** | The short name of the hierarchy item. If this attribute is set, the &#x60;weight&#x60; and the &#x60;formattedWeight&#x60; are &#x60;null&#x60;. | 
**weight** | **str** | The accurate weight of the hierarchy item. As a decimal precision number it is written as a string to not loose precision with conversion to a floating point number. If this attribute is set, the &#x60;short&#x60; is null. | 
**formatted_weight** | **str** | The formatted weight of the hierarchy item. The standard formatting of the OpenProject server is used to convert this number into a representable format - i.e. falling back to scientific notation for very small and very big numbers. If this attribute is set, the &#x60;short&#x60; is null. | 
**depth** | **int** | The hierarchy depth. The root item has a depth of 0. | 
**links** | [**HierarchyItemReadModelLinks**](HierarchyItemReadModelLinks.md) |  | 

## Example

```python
from openproject_client.models.hierarchy_item_read_model import HierarchyItemReadModel

# TODO update the JSON string below
json = "{}"
# create an instance of HierarchyItemReadModel from a JSON string
hierarchy_item_read_model_instance = HierarchyItemReadModel.from_json(json)
# print the JSON string representation of the object
print(HierarchyItemReadModel.to_json())

# convert the object into a dict
hierarchy_item_read_model_dict = hierarchy_item_read_model_instance.to_dict()
# create an instance of HierarchyItemReadModel from a dict
hierarchy_item_read_model_from_dict = HierarchyItemReadModel.from_dict(hierarchy_item_read_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


