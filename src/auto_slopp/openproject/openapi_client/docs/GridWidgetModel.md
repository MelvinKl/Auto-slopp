# GridWidgetModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**id** | **int** | The grid widget&#39;s unique identifier. Can be null, if a new widget is created within a grid. | 
**identifier** | **str** | An alternative, human legible, and unique identifier. | 
**start_row** | **int** | The index of the starting row of the widget. The row is inclusive. | 
**end_row** | **int** | The index of the ending row of the widget. The row is exclusive. | 
**start_column** | **int** | The index of the starting column of the widget. The column is inclusive. | 
**end_column** | **int** | The index of the ending column of the widget. The column is exclusive. | 
**options** | **object** |  | [optional] 

## Example

```python
from auto_slopp.openproject.openapi_client.models.grid_widget_model import GridWidgetModel

# TODO update the JSON string below
json = "{}"
# create an instance of GridWidgetModel from a JSON string
grid_widget_model_instance = GridWidgetModel.from_json(json)
# print the JSON string representation of the object
print(GridWidgetModel.to_json())

# convert the object into a dict
grid_widget_model_dict = grid_widget_model_instance.to_dict()
# create an instance of GridWidgetModel from a dict
grid_widget_model_from_dict = GridWidgetModel.from_dict(grid_widget_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


