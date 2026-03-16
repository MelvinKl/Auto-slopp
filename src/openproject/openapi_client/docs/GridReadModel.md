# GridReadModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**id** | **int** | Grid&#39;s id | 
**row_count** | **int** | The number of rows the grid has | 
**column_count** | **int** | The number of columns the grid has | 
**widgets** | [**List[GridWidgetModel]**](GridWidgetModel.md) | The set of &#x60;GridWidget&#x60;s selected for the grid.  # Conditions  - The widgets must not overlap. | 
**created_at** | **datetime** | The time the grid was created. | [optional] 
**updated_at** | **datetime** | The time the grid was last updated. | [optional] 
**links** | [**GridReadModelLinks**](GridReadModelLinks.md) |  | 

## Example

```python
from openproject_client.models.grid_read_model import GridReadModel

# TODO update the JSON string below
json = "{}"
# create an instance of GridReadModel from a JSON string
grid_read_model_instance = GridReadModel.from_json(json)
# print the JSON string representation of the object
print(GridReadModel.to_json())

# convert the object into a dict
grid_read_model_dict = grid_read_model_instance.to_dict()
# create an instance of GridReadModel from a dict
grid_read_model_from_dict = GridReadModel.from_dict(grid_read_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


