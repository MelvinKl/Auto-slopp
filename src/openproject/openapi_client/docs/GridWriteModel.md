# GridWriteModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**row_count** | **int** | The number of rows the grid has | [optional] 
**column_count** | **int** | The number of columns the grid has | [optional] 
**widgets** | [**List[GridWidgetModel]**](GridWidgetModel.md) | The set of &#x60;GridWidget&#x60;s selected for the grid.  # Conditions  - The widgets must not overlap. | [optional] 
**links** | [**GridWriteModelLinks**](GridWriteModelLinks.md) |  | [optional] 

## Example

```python
from openproject_client.models.grid_write_model import GridWriteModel

# TODO update the JSON string below
json = "{}"
# create an instance of GridWriteModel from a JSON string
grid_write_model_instance = GridWriteModel.from_json(json)
# print the JSON string representation of the object
print(GridWriteModel.to_json())

# convert the object into a dict
grid_write_model_dict = grid_write_model_instance.to_dict()
# create an instance of GridWriteModel from a dict
grid_write_model_from_dict = GridWriteModel.from_dict(grid_write_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


